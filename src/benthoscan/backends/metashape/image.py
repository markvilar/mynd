"""Module for image functionality for the Metashape backend."""

from collections.abc import Callable
from functools import partial

import Metashape
import numpy as np

from .data_types import CameraPair, ImagePair, LabelledImage


def _image_dtype_to_numpy(image: Metashape.Image) -> np.dtype:
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


def image_to_numpy(image: Metashape.Image) -> np.ndarray:
    """Converts a Metashape image to a Numpy array."""

    data_type: np.dtype = _image_dtype_to_numpy(image)

    image_array = np.frombuffer(image.tostring(), dtype=data_type)
    assert len(image_array) == image.height * image.width * image.cn
    image_array: np.ndarray = image_array.reshape(image.height, image.width, image.cn)

    return np.squeeze(image_array)


ImagePairLoader = Callable[[None], ImagePair]


def generate_image_loaders(camera_pairs: list[CameraPair]) -> list[ImagePairLoader]:
    """Metashape - Generates a list of image loaders for the given camera pairs."""
    
    image_loaders: list[ImagePairLoader] = [
        partial(load_image_pair, camera_pair=pair) for pair in camera_pairs
    ]
    
    return image_loaders


def load_image_pair(camera_pair: CameraPair) -> ImagePair:
    """Loads a pair of images."""

    first_image: np.ndarray = np.squeeze(image_to_numpy(camera_pair.master.image()))
    second_image: np.ndarray = np.squeeze(image_to_numpy(camera_pair.slave.image()))

    return ImagePair(
        first = LabelledImage(camera_pair.first.label, first_image),
        second = LabelledImage(camera_pair.second.label, second_image),
    )
