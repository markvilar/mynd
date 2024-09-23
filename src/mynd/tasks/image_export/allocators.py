"""Module for memory allocators."""

from collections.abc import Iterable
from typing import NamedTuple

import h5py
import numpy as np

from ...camera import ImageBundle, ImageBundleLoader
from ...utils.result import Ok, Err, Result

from .bundle_validators import (
    ImageBundleTemplate,
    check_image_bundle_fits_template,
)


class ImageBundleBuffers(NamedTuple):
    """Class representing image bundle buffers."""

    labels: np.ndarray
    intensities: np.ndarray
    ranges: np.ndarray
    normals: np.ndarray


def allocate_buffers(template: ImageBundleTemplate, count: int) -> ImageBundleBuffers:
    """Allocates buffers for a given number of image bundles."""
    return ImageBundleBuffers(
        labels=np.empty(shape=(count,), dtype=np.dtypes.StringDType()),
        intensities=np.empty(
            shape=(count,) + template.intensities.shape,
            dtype=template.intensities.dtype,
        ),
        ranges=np.empty(
            shape=(count,) + template.ranges.shape, dtype=template.ranges.dtype
        ),
        normals=np.empty(
            shape=(count,) + template.normals.shape,
            dtype=template.normals.dtype,
        ),
    )


def load_bundle_buffers(
    template: ImageBundleTemplate,
    loaders: Iterable[ImageBundleLoader],
) -> Result[ImageBundleBuffers, str]:
    """Load bundles into a buffer."""

    count: int = len(loaders)

    buffers: ImageBundleBuffers = allocate_buffers(template, count)

    for index, loader in enumerate(loaders):
        bundle: ImageBundle = loader()

        fits_template: bool = check_image_bundle_fits_template(bundle, template)
        if not fits_template:
            return Err(f"image bundle {bundle.label} does not fit template")

        buffers.labels[index] = bundle.label
        buffers.intensities[index] = bundle.intensities.data
        buffers.ranges[index] = bundle.ranges.data
        buffers.normals[index] = bundle.normals.data

    return Ok(buffers)


def allocate_datasets(
    group: h5py.Group, template: ImageBundleTemplate, count: int
) -> None:
    """Allocate datasets for the given template and count."""

    group.create_dataset("labels", shape=(count,), dtype=h5py.string_dtype())
    group.create_dataset(
        "intensities",
        shape=(count,) + template.intensities.shape,
        dtype=template.intensities.dtype,
    )
    group.create_dataset(
        "ranges",
        shape=(count,) + template.ranges.shape,
        dtype=template.ranges.dtype,
    )
    group.create_dataset(
        "normals",
        shape=(count,) + template.normals.shape,
        dtype=template.normals.dtype,
    )
