"""Module for common image processors."""

import cv2

from .image_types import Image


def flip_image(image: Image, axis: int = 1) -> Image:
    """Flip an image around the specified axis."""
    flipped: Image = Image.from_array(
        data=cv2.flip(image.to_array(), axis),
        pixel_format=image.pixel_format,
    )
    return flipped


def resize_image(image: Image, height: int, width: int) -> Image:
    """Resize an image to the desired size. The size is specified as HxW"""
    return Image.from_array(
        data=cv2.resize(image.to_array(), (width, height), cv2.INTER_AREA),
        pixel_format=image.pixel_format,
    )
