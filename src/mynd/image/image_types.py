"""Module for image data."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Self, TypeAlias, TypeVar

import numpy as np


class PixelFormat(StrEnum):
    """Class representing an image format."""

    GRAY = auto()
    X = auto()
    RGB = auto()
    BGR = auto()
    XYZ = auto()
    RGBA = auto()
    BGRA = auto()


@dataclass(frozen=True)
class ImageLayout:
    """Class representing an image layout."""

    height: int
    width: int
    channels: int

    @property
    def shape(self: Self) -> tuple[int, int, int]:
        """Returns the shape of the image layout."""
        return (self.height, self.width, self.channels)


# Create a generic variable that can be 'Parent', or any subclass.
T: TypeVar = TypeVar("T", bound="Image")


@dataclass(frozen=True)
class Image:
    """Class representing an image."""

    _data: np.ndarray
    _pixel_format: PixelFormat
    _layout: ImageLayout

    @property
    def pixel_format(self: Self) -> PixelFormat:
        """Returns the pixel format of the image."""
        return self._pixel_format

    @property
    def layout(self: Self) -> ImageLayout:
        """Return the layout of the image."""
        return self._layout

    @property
    def height(self: Self) -> int:
        """Returns the height of the image."""
        return self._layout.height

    @property
    def width(self: Self) -> int:
        """Returns the height of the image."""
        return self._layout.width

    @property
    def channels(self: Self) -> int:
        """Returns the height of the image."""
        return self._layout.channels

    @property
    def shape(self: Self) -> tuple[int, int, int]:
        """Returns the shape of the image."""
        return (self.height, self.width, self.channels)

    @property
    def dtype(self: Self) -> np.dtype:
        """Returns the data type of the image."""
        return self._data.dtype

    @property
    def ndim(self: Self) -> int:
        """Returns the number of dimension of the image."""
        return self._data.ndim

    @classmethod
    def from_array(
        cls: type[T], data: np.ndarray, pixel_format: PixelFormat
    ) -> T:
        """Creates an image from an array."""
        layout: ImageLayout = ImageLayout(
            height=data.shape[0], width=data.shape[1], channels=data.shape[2]
        )
        return cls(data, pixel_format, layout)

    def to_array(self: Self) -> np.ndarray:
        """Returns the image pixels as an array."""
        return self._data.copy()

    def copy(self: Self) -> T:
        """Returns a copy of the image."""
        return Image(self._data, self._pixel_format, self._layout)


ImageLoader = Callable[[None], Image]


@dataclass
class ImageBundle:
    """Class representing an image bundle with intensities, ranges, and normals."""

    intensities: Image
    ranges: Image
    normals: Image


ImageBundleLoader: TypeAlias = Callable[[None], ImageBundle]
