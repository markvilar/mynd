"""Module for image functionality for the Metashape backend."""

from collections.abc import Iterable
from functools import partial

import Metashape as ms
import numpy as np

from ....camera import Image, ImageFormat, ImageLoader
from ....containers import Pair


def convert_image(image: ms.Image) -> Image:
    """Converts a Metashape image to an internal image."""

    format: ImageFormat = _get_format_from_image(image)
    data: np.ndarray = _image_buffer_to_array(image)

    return Image(data=data, format=format)


def load_camera_image(camera: ms.Camera) -> Image:
    """Load an image from a Metashape camera."""
    image: Image = convert_image(camera.image())
    image.label: str = camera.label
    return image


def generate_image_loader(camera: ms.Camera) -> ImageLoader:
    """Generate an image loader from a Metashape camera."""
    return partial(load_camera_image, camera=camera)


ImagePair = Pair[Image]
CameraPair = Pair[ms.Camera]


def generate_image_loader_pairs(
    camera_pairs: Iterable[CameraPair],
) -> list[Pair[ImageLoader]]:
    """Generate image loaders for a collection of camera pairs."""

    loaders: list[Pair[ImageLoader]] = [
        Pair(generate_image_loader(pair.first), generate_image_loader(pair.second))
        for pair in camera_pairs
    ]

    return loaders


def _image_dtype_to_numpy(image: ms.Image) -> np.dtype:
    """Converts a Metashape image data type to a Numpy dtype."""

    match image.data_type:
        case "U8":
            return np.uint8
        case "U16":
            return np.uint16
        case "U32":
            return np.uint32
        case "U64":
            return np.uint64
        case "F16":
            return np.float16
        case "F32":
            return np.float32
        case "F64":
            return np.float64
        case _:
            raise NotImplementedError("unknown data type in convert_data_type_to_numpy")


def _get_format_from_image(image: ms.Image) -> ImageFormat:
    """Returns an image format based on the image channels."""

    channels: str = image.channels.lower()

    match channels:
        case "gray" | "i":
            return ImageFormat.GRAY
        case "x":
            return ImageFormat.X
        case "rgb":
            return ImageFormat.RGB
        case "bgr":
            return ImageFormat.BGR
        case "xyz":
            return ImageFormat.XYZ
        case "rgba":
            return ImageFormat.RGBA
        case "bgra":
            return ImageFormat.BGRA
        case _:
            return ImageFormat.UNKNOWN


def _image_buffer_to_array(image: ms.Image) -> np.ndarray:
    """Converts a Metashape image to a Numpy array."""

    data_type: np.dtype = _image_dtype_to_numpy(image)

    image_array = np.frombuffer(image.tostring(), dtype=data_type)
    assert len(image_array) == image.height * image.width * image.cn
    image_array: np.ndarray = image_array.reshape(image.height, image.width, image.cn)

    return np.squeeze(image_array)
