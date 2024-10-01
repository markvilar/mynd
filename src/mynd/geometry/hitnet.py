"""Module for functionality related to Hitnet disparity estimation model."""

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import cv2
import numpy as np
import onnxruntime as onnxrt

from ..image import Image, ImageFormat
from ..containers import Pair
from ..utils.result import Ok, Err, Result


class Argument(NamedTuple):
    """Class representing an argument."""

    name: str
    shape: tuple
    type: type


@dataclass
class HitnetConfig:
    """Class representing a Hitnet config."""

    session: onnxrt.InferenceSession

    @property
    def inputs(self) -> list[Argument]:
        """Returns the inputs of the session."""
        arguments = self.session.get_inputs()
        return [
            Argument(argument.name, tuple(argument.shape), argument.type)
            for argument in arguments
        ]

    @property
    def outputs(self) -> list[Argument]:
        """Returns the inputs of the session."""
        arguments = self.session.get_outputs()
        return [
            Argument(argument.name, tuple(argument.shape), argument.type)
            for argument in arguments
        ]

    @property
    def input_size(self) -> tuple[int, int]:
        """Returns the expected input size for the model as (H, W)."""
        tensor_argument: Argument = self.inputs[0]
        batch, channels, height, width = tensor_argument.shape
        return (height, width)


def load_hitnet(path: Path) -> Result[HitnetConfig, str]:
    """Loads a Hitnet model from an ONNX file."""

    if not path.exists():
        return Err(f"model path does not exist: {path}")
    if not path.suffix == ".onnx":
        return Err(f"model path is not an ONNX file: {path}")

    session: onnxrt.InferenceSession = onnxrt.InferenceSession(
        str(path), providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )

    # TODO: Add validation based on session input and output

    return Ok(HitnetConfig(session=session))


def _preprocess_images(
    config: HitnetConfig, left: Image, right: Image
) -> tuple[np.ndarray, np.ndarray]:
    """Preprocess input images for HITNET."""

    match left.format:
        case ImageFormat.RGB:
            left_array: np.ndarray = cv2.cvtColor(left.to_array(), cv2.COLOR_RGB2GRAY)
        case ImageFormat.BGR:
            left_array: np.ndarray = cv2.cvtColor(left.to_array(), cv2.COLOR_BGR2GRAY)
        case ImageFormat.GRAY:
            left_array: np.ndarray = left.to_array()
        case _:
            raise NotImplementedError(f"invalid image format: {left.format}")

    match right.format:
        case ImageFormat.RGB:
            right_array: np.ndarray = cv2.cvtColor(right.to_array(), cv2.COLOR_RGB2GRAY)
        case ImageFormat.BGR:
            right_array: np.ndarray = cv2.cvtColor(right.to_array(), cv2.COLOR_BGR2GRAY)
        case ImageFormat.GRAY:
            right_array: np.ndarray = right.to_array()
        case _:
            raise NotImplementedError(f"invalid image format: {right.format}")

    # NOTE: Images should now be grayscale

    assert len(config.inputs) == 1, f"invalid number of inputs: {len(config.inputs)}"
    assert len(config.outputs) == 1, f"invalid number of outputs: {len(config.outputs)}"

    height, width = config.input_size

    left_array: np.ndarray = cv2.resize(left_array, (width, height), cv2.INTER_AREA)
    right_array: np.ndarray = cv2.resize(right_array, (width, height), cv2.INTER_AREA)

    # Grayscale needs expansion to reach H,W,C.
    # Need to do that now because resize would change the shape.
    if left_array.ndim == 2:
        left_array: np.ndarray = np.expand_dims(left_array, axis=-1)
    if right_array.ndim == 2:
        right_array: np.ndarray = np.expand_dims(right_array, axis=-1)

    # TODO: Get normalization value based on image dtype

    # -> H,W,C=2 or 6 , normalized to [0,1]
    tensor = np.concatenate((left_array, right_array), axis=-1) / 255.0
    # -> C,H,W
    tensor = tensor.transpose(2, 0, 1)
    # -> B=1,C,H,W
    tensor = np.expand_dims(tensor, 0).astype(np.float32)

    return tensor


def _postprocess_disparity(
    disparity: np.ndarray, image: Image, flip: bool = False
) -> np.ndarray:
    """Postprocess the disparity map by resizing it to match the original image,
    adjusting the disparity with the width ratio, and optionally flipping the disparity
    horizontally."""

    # Squeeze disparity to a 2D array
    disparity: np.ndarray = np.squeeze(disparity)

    # Scale disparities by the width ratios between the original images and the disparity maps
    scale: float = float(image.width) / float(disparity.shape[1])
    disparity *= scale

    # Resize disparity maps to the original image sizes
    disparity: np.ndarray = cv2.resize(
        disparity, (image.width, image.height), cv2.INTER_AREA
    )

    # If enabled, flip disparity map around y-axis (horizontally)
    if flip:
        disparity: np.ndarray = cv2.flip(disparity, 1)

    return disparity


def compute_disparity(
    config: HitnetConfig, left: Image, right: Image
) -> Pair[np.ndarray]:
    """Computes the disparity for a pair of stereo images. The images needs to be
    rectified prior to disparity estimation. Returns the left and right disparity as
    arrays with float32 values."""

    # Create tensor from flipped images to get left disparity
    flipped_left: Image = Image(
        data=cv2.flip(left.to_array(), 1),
        format=left.format,
    )
    flipped_right: Image = Image(
        data=cv2.flip(right.to_array(), 1),
        format=right.format,
    )

    tensor: np.ndarray = _preprocess_images(config, left, right)
    flipped_tensor: np.ndarray = _preprocess_images(config, flipped_right, flipped_left)

    left_outputs: list[np.ndarray] = config.session.run(
        ["reference_output_disparity"], {"input": tensor}
    )
    right_outputs: list[np.ndarray] = config.session.run(
        ["reference_output_disparity"], {"input": flipped_tensor}
    )

    # Since we estimate the right disparity from the flipped images, we need to flip the
    # right disparity map back to the same perspective as the original rigth image
    left_disparity: np.ndarray = _postprocess_disparity(
        left_outputs[0], left, flip=False
    )
    right_disparity: np.ndarray = _postprocess_disparity(
        right_outputs[0], right, flip=True
    )

    return Pair(first=left_disparity, second=right_disparity)
