"""Unit tests for the image package."""

import pytest
import numpy as np

from mynd.image import Image, ImageLayout, PixelFormat


def test_pixel_format():
    assert PixelFormat.GRAY.value == "gray"
    assert PixelFormat.RGB.value == "rgb"
    assert PixelFormat.RGBA.value == "rgba"


def test_image_layout():
    layout = ImageLayout(height=100, width=200, channels=3)
    assert layout.height == 100
    assert layout.width == 200
    assert layout.channels == 3
    assert layout.shape == (100, 200, 3)


def test_image_creation():
    data = np.zeros((100, 200, 3), dtype=np.uint8)
    image = Image.from_array(data, PixelFormat.RGB)
    assert image.pixel_format == PixelFormat.RGB
    assert image.layout.height == 100
    assert image.layout.width == 200
    assert image.layout.channels == 3
    assert image.shape == (100, 200, 3)
    assert image.dtype == np.uint8
    assert image.ndim == 3


def test_image_properties():
    data = np.zeros((50, 60, 4), dtype=np.float32)
    image = Image.from_array(data, PixelFormat.RGBA)
    assert image.height == 50
    assert image.width == 60
    assert image.channels == 4
    assert image.shape == (50, 60, 4)
    assert image.dtype == np.float32


def test_image_to_array():
    original_data = np.random.rand(30, 40, 3)
    image = Image.from_array(original_data, PixelFormat.RGB)
    retrieved_data = image.to_array()
    assert np.array_equal(original_data, retrieved_data)
    assert id(original_data) != id(retrieved_data)  # Ensure it's a copy


def test_image_copy():
    data = np.zeros((20, 30, 1), dtype=np.uint8)
    original_image = Image.from_array(data, PixelFormat.GRAY)
    copied_image = original_image.copy()
    assert original_image.shape == copied_image.shape
    assert original_image.pixel_format == copied_image.pixel_format
    assert id(original_image) != id(copied_image)  # Ensure it's a new object


def test_invalid_image_creation():
    with pytest.raises(IndexError):
        # This should raise an error because the array doesn't have 3 dimensions
        Image.from_array(np.zeros((100, 200)), PixelFormat.RGB)


def test_image_layout_immutability():
    layout = ImageLayout(height=100, width=200, channels=3)
    with pytest.raises(AttributeError):
        layout.height = (
            50  # This should raise an error because ImageLayout is frozen
        )


def test_image_immutability():
    data = np.zeros((100, 200, 3), dtype=np.uint8)
    image = Image.from_array(data, PixelFormat.RGB)
    with pytest.raises(AttributeError):
        image._data = np.ones(
            (100, 200, 3)
        )  # This should raise an error because Image is frozen
