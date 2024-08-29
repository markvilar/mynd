"""Module for image data."""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Optional

import cv2
import numpy as np


class ImageFormat(StrEnum):
    """Class representing an image format."""

    GRAY = auto()
    X = auto()

    RGB = auto()
    BGR = auto()
    XYZ = auto()

    RGBA = auto()
    BGRA = auto()

    UNKNOWN = auto()


@dataclass
class Image:
    """Class representing a labelled image."""

    data: np.ndarray
    format: ImageFormat
    label: Optional[str] = None

    @property
    def dtype(self) -> np.dtype:
        """Returns the data type of the image."""
        return self.data.dtype

    @property
    def height(self) -> int:
        """Returns the height of the image."""
        return self.data.shape[0]

    @property
    def width(self) -> int:
        """Returns the height of the image."""
        return self.data.shape[1]

    @property
    def channels(self) -> int:
        """Returns the height of the image."""
        return self.data.shape[2]

    def to_array(self) -> np.ndarray:
        """Returns the image pixels as an array."""
        return self.data.copy()


def flip_image(image: Image, axis: int) -> Image:
    """Flip an image around the specified axis."""
    flipped: Image = Image(
        data=cv2.flip(image.to_array(), 1),
        format=image.format,
        label=image.label,
    )
    return flipped


def resize_image(image: Image, size: tuple[int, int]) -> Image:
    """Resize an image to the desired size. The size is specified as HxW"""
    height, width = size
    return Image(
        data=cv2.resize(image.to_array(), (width, height), cv2.INTER_AREA),
        format=image.format,
        label=image.label,
    )
