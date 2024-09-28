"""Module for templates to validate image bundles."""

from dataclasses import dataclass

import numpy as np

from ...camera import Image, ImageFormat, ImageBundle


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


def check_image_bundle_fits_template(
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
