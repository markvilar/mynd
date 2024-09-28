"""Module for memory allocators."""

from dataclasses import dataclass

import h5py
import numpy as np

from ...database import H5Database

from .bundle_templates import ImageBundleTemplate


@dataclass
class ImageBundleBuffers:
    """Class representing image bundle buffers."""

    labels: np.ndarray
    intensities: np.ndarray
    ranges: np.ndarray
    normals: np.ndarray


@dataclass
class ImageBundleDatasets:
    """Class representing image bundle datasets."""

    labels: H5Database.Group
    intensities: H5Database.Group
    ranges: H5Database.Group
    normals: H5Database.Group


def allocate_bundle_buffers(
    template: ImageBundleTemplate, count: int
) -> ImageBundleBuffers:
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


def allocate_bundle_datasets(
    group: H5Database.Group, template: ImageBundleTemplate, count: int
) -> ImageBundleDatasets:
    """Allocate datasets for the given template and count."""

    labels = group.create_dataset("labels", shape=(count,), dtype=h5py.string_dtype())
    intensities = group.create_dataset(
        "intensities",
        shape=(count,) + template.intensities.shape,
        dtype=template.intensities.dtype,
    )
    ranges = group.create_dataset(
        "ranges",
        shape=(count,) + template.ranges.shape,
        dtype=template.ranges.dtype,
    )
    normals = group.create_dataset(
        "normals",
        shape=(count,) + template.normals.shape,
        dtype=template.normals.dtype,
    )

    return ImageBundleDatasets(labels, intensities, ranges, normals)
