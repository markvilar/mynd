"""Module for functionality related to Hitnet disparity estimation model."""

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import cv2
import numpy as np
import torch
import onnxruntime as onnxrt

from mynd.image import Image, PixelFormat, flip_image
from mynd.utils.containers import Pair
from mynd.utils.result import Ok, Err, Result

from .stereo_matcher import StereoMatcher


class Argument(NamedTuple):
    """Class representing an argument."""

    name: str
    shape: tuple
    type: type


@dataclass
class HitnetModel:
    """Class representing a Hitnet model."""

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


def load_hitnet(path: Path) -> Result[HitnetModel, str]:
    """Loads a Hitnet model from an ONNX file."""

    if not path.exists():
        return Err(f"model path does not exist: {path}")
    if not path.suffix == ".onnx":
        return Err(f"model path is not an ONNX file: {path}")

    providers: list = [
        (
            "CUDAExecutionProvider",
            {
                "device_id": torch.cuda.current_device(),
                "user_compute_stream": str(
                    torch.cuda.current_stream().cuda_stream
                ),
            },
        )
    ]

    sess_options: onnxrt.SessionOptions = onnxrt.SessionOptions()

    session: onnxrt.InferenceSession = onnxrt.InferenceSession(
        str(path),
        sess_options=sess_options,
        providers=providers,
    )

    # TODO: Add validation based on session input and output

    return Ok(HitnetModel(session=session))


def create_hitnet_matcher(path: Path) -> StereoMatcher:
    """Creates a Hitnet stereo matcher."""

    model: HitnetModel = load_hitnet(path).unwrap()

    def match_stereo_hitnet(left: Image, right: Image) -> Pair[np.ndarray]:
        """Matches a pair of rectified stereo images with the Hitnet model."""
        return _compute_disparity(model, left, right)

    return match_stereo_hitnet


def _preprocess_images(
    model: HitnetModel, left: Image, right: Image
) -> tuple[np.ndarray, np.ndarray]:
    """Preprocess input images for HITNET."""

    match left.pixel_format:
        case PixelFormat.RGB:
            left_array: np.ndarray = cv2.cvtColor(
                left.to_array(), cv2.COLOR_RGB2GRAY
            )
        case PixelFormat.BGR:
            left_array: np.ndarray = cv2.cvtColor(
                left.to_array(), cv2.COLOR_BGR2GRAY
            )
        case PixelFormat.GRAY:
            left_array: np.ndarray = left.to_array()
        case _:
            raise NotImplementedError(
                f"invalid image format: {left.pixel_format}"
            )

    match right.pixel_format:
        case PixelFormat.RGB:
            right_array: np.ndarray = cv2.cvtColor(
                right.to_array(), cv2.COLOR_RGB2GRAY
            )
        case PixelFormat.BGR:
            right_array: np.ndarray = cv2.cvtColor(
                right.to_array(), cv2.COLOR_BGR2GRAY
            )
        case PixelFormat.GRAY:
            right_array: np.ndarray = right.to_array()
        case _:
            raise NotImplementedError(
                f"invalid image format: {right.pixel_format}"
            )

    # NOTE: Images should now be grayscale

    assert (
        len(model.inputs) == 1
    ), f"invalid number of inputs: {len(model.inputs)}"
    assert (
        len(model.outputs) == 1
    ), f"invalid number of outputs: {len(model.outputs)}"

    height, width = model.input_size

    left_array: np.ndarray = cv2.resize(
        left_array, (width, height), cv2.INTER_AREA
    )
    right_array: np.ndarray = cv2.resize(
        right_array, (width, height), cv2.INTER_AREA
    )

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


def _compute_disparity(
    model: HitnetModel, left: Image, right: Image
) -> Pair[np.ndarray]:
    """Computes the disparity for a pair of stereo images. The images needs to be
    rectified prior to disparity estimation. Returns the left and right disparity as
    arrays with float32 values."""

    # Create tensor from flipped images to get left disparity
    flipped_left: Image = flip_image(left)
    flipped_right: Image = flip_image(right)

    tensor: np.ndarray = _preprocess_images(model, left, right)
    flipped_tensor: np.ndarray = _preprocess_images(
        model, flipped_right, flipped_left
    )

    left_outputs: list[np.ndarray] = model.session.run(
        ["reference_output_disparity"], {"input": tensor}
    )
    right_outputs: list[np.ndarray] = model.session.run(
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
