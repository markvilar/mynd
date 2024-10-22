"""Module for common image processors."""

import cv2
import numpy as np

from .image_types import Image, PixelFormat


def flip_image(image: Image, axis: int = 1) -> Image:
    """Flip an image around the specified axis."""
    flipped_values: np.ndarray = cv2.flip(image.to_array(), axis)
    flipped: Image = Image.from_array(
        data=flipped_values,
        pixel_format=image.pixel_format,
    )
    return flipped


def resize_image(image: Image, height: int, width: int) -> Image:
    """Resize an image to the desired size. The size is specified as HxW"""
    return Image.from_array(
        data=cv2.resize(image.to_array(), (width, height), cv2.INTER_AREA),
        pixel_format=image.pixel_format,
    )


def filter_image_clahe(image: Image, size: int, clip: float) -> Image:
    """Filter an image with CLAHE."""

    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(size, size))

    match image.pixel_format:
        case PixelFormat.GRAY:
            return _filter_image_clahe_gray(image, clahe)
        case PixelFormat.RGB | PixelFormat.BGR:
            return _filter_image_clahe_rgb(image, clahe)
        case _:
            raise NotImplementedError(
                f"invalid pixel format: {image.pixel_format}"
            )

    raise NotImplementedError


def _filter_image_clahe_rgb(image: Image, processor: object) -> Image:
    """Applies CLAHE to a RGB / BGR image via LAB color space."""

    match image.pixel_format:
        case PixelFormat.RGB:
            format_to = cv2.COLOR_RGB2LAB
            format_from = cv2.COLOR_LAB2RGB
        case PixelFormat.BGR:
            format_to = cv2.COLOR_BGR2LAB
            format_from = cv2.COLOR_LAB2BGR
        case _:
            raise NotImplementedError

    values: np.ndarray = cv2.cvtColor(image.to_array(), format_to)
    values[:, :, 0]: np.ndarray = processor.apply(values[:, :, 0])
    values: np.ndarray = cv2.cvtColor(values, format_from)

    return Image.from_array(values, image.pixel_format)


def _filter_image_clahe_gray(image: Image, processor: object) -> Image:
    """Applies CLAHE to a grayscale image."""
    values: np.ndarray = image.to_array()
    values: np.ndarray = processor.apply(values)
    return Image.from_array(values, image.pixel_format)
