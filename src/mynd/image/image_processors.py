"""Module for common image processors."""

import cv2

from .image_types import Image


def flip_image(image: Image, axis: int) -> Image:
    """Flip an image around the specified axis."""
    flipped: Image = Image(
        data=cv2.flip(image.to_array(), 1),
        format=image.format,
    )
    return flipped


def resize_image(image: Image, size: tuple[int, int]) -> Image:
    """Resize an image to the desired size. The size is specified as HxW"""
    height, width = size
    return Image(
        data=cv2.resize(image.to_array(), (width, height), cv2.INTER_AREA),
        format=image.format,
    )
