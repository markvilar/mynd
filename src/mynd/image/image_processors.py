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


def _convert_grayscale_to_rgb(image: Image) -> Image:
    """Converts a grayscale image to RGB."""
    values: np.ndarray = cv2.cvtColor(image.to_array(), cv2.COLOR_GRAY2RGB)
    return Image.from_array(values, PixelFormat.RGB)


def convert_to_rgb(image: Image) -> Image:
    """Converts an image to RGB."""
    match image.pixel_format:
        case PixelFormat.GRAY:
            return _convert_grayscale_to_rgb(image)
        case PixelFormat.RGB:
            return image
        case _:
            raise NotImplementedError("invalid image pixel format")


def normalize_image(
    image: Image, lower: int | float, upper: int | float, flip: bool = False
) -> Image:
    """Normalizes the values of an image to be between the lower and upper values."""
    values: np.ndarray = image.to_array()

    values[values > upper] = upper
    values[values < lower] = lower

    min_value: float = values.min()
    max_value: float = values.max()

    # TODO: Add support for multiple dtypes here
    if flip:
        scale: int = -255
        offset: int = 255
    else:
        scale: int = 255
        offset: int = 0

    # Normalized values between 0 and 1
    normalized: np.ndarray = (values - min_value) / (max_value - min_value)
    normalized: np.ndarray = scale * normalized + offset

    normalized: np.ndarray = normalized.astype(np.uint8)
    return Image.from_array(normalized, image.pixel_format)


def apply_color_map(image: Image) -> Image:
    """Applies a color map to the image values."""
    values: np.ndarray = cv2.applyColorMap(image.to_array(), cv2.COLORMAP_JET)
    return Image.from_array(values, PixelFormat.RGB)
