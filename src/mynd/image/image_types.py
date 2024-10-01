"""Module for image data."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Self, TypeAlias

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


@dataclass(frozen=True)
class Image:
    """Class representing a labelled image."""

    data: np.ndarray
    format: ImageFormat

    @property
    def height(self: Self) -> int:
        """Returns the height of the image."""
        return self.data.shape[0]

    @property
    def width(self: Self) -> int:
        """Returns the height of the image."""
        return self.data.shape[1]

    @property
    def channels(self: Self) -> int:
        """Returns the height of the image."""
        return self.data.shape[2]

    @property
    def shape(self: Self) -> tuple[int, int, int]:
        """Returns the shape of the image."""
        return self.data.shape

    @property
    def dtype(self: Self) -> np.dtype:
        """Returns the data type of the image."""
        return self.data.dtype

    @property
    def ndim(self: Self) -> int:
        """Returns the number of dimension of the image."""
        return self.data.ndim

    def to_array(self: Self) -> np.ndarray:
        """Returns the image pixels as an array."""
        return self.data.copy()


ImageLoader = Callable[[None], Image]


@dataclass
class ImageBundle:
    """Class representing an image bundle with intensities, ranges, and normals."""

    intensities: Image
    ranges: Image
    normals: Image


ImageBundleLoader: TypeAlias = Callable[[None], ImageBundle]
