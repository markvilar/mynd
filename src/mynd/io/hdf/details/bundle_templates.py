"""Module for templates to validate image bundles."""

from dataclasses import dataclass
from typing import Callable

import numpy as np

from ....image import Image, ImageFormat, ImageBundle


@dataclass
class ImageTemplate:
    """Class representing an image template with shape, format, and dtype."""

    shape: tuple[int, int, int]
    format: ImageFormat
    dtype: np.dtype


@dataclass
class ImageBundleTemplate:
    """Class representing a template with sizes, formats, and dtypes for image bundles."""

    intensities: ImageTemplate
    ranges: ImageTemplate
    normals: ImageTemplate


def create_image_bundle_template(bundle: ImageBundle) -> ImageBundleTemplate:
    """Creates an image bundle template from an image bundle."""
    return ImageBundleTemplate(
        intensities=_create_image_template(bundle.intensities),
        ranges=_create_image_template(bundle.ranges),
        normals=_create_image_template(bundle.normals),
    )


ImageBundleValidator = Callable[[ImageBundle], bool]


def create_image_bundle_validator(
    template: ImageBundleTemplate,
) -> ImageBundleValidator:
    """Creates an image bundle validator based on a bundle template."""

    def validate_bundle_with_template(bundle: ImageBundle) -> bool:
        """Validates an image bundle by checking if it fits the image bundle template."""
        return _check_image_bundle_fits_template(bundle, template)

    return validate_bundle_with_template


def _check_image_bundle_fits_template(
    bundle: ImageBundle, template: ImageBundleTemplate
) -> bool:
    """Checks whether the image bundle fits the given template."""
    checks: list[bool] = [
        _check_image_fits_template(bundle.intensities, template.intensities),
        _check_image_fits_template(bundle.ranges, template.ranges),
        _check_image_fits_template(bundle.normals, template.normals),
    ]
    return any(checks)


def _create_image_template(image: Image) -> ImageTemplate:
    """Creates an image template from an image."""
    return ImageTemplate(shape=image.shape, format=image.format, dtype=image.dtype)


def _check_image_fits_template(image: Image, template: ImageTemplate) -> bool:
    """Checks whether the image fits the given template."""
    checks: list[bool] = [
        image.shape == template.shape,
        image.format == template.format,
        image.dtype == template.dtype,
    ]
    return any(checks)
