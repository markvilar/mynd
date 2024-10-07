"""Module for memory allocators."""

from dataclasses import dataclass
from typing import Self

import numpy as np

from ..database import H5Database
from .bundle_templates import ImageBundleTemplate


@dataclass
class ImageBundleBuffers:
    """Class representing image bundle buffers."""

    intensities: np.ndarray
    ranges: np.ndarray
    normals: np.ndarray

    def bundle_count(self: Self) -> int:
        """Returns the number of bundles in the buffers."""
        return len(self.intensities)


@dataclass
class ImageBundleStorage:
    """Class representing image bundle datasets."""

    intensities: H5Database.Group
    ranges: H5Database.Group
    normals: H5Database.Group


def allocate_bundle_buffers(
    template: ImageBundleTemplate, count: int
) -> ImageBundleBuffers:
    """Allocates buffers for a given number of image bundles."""
    return ImageBundleBuffers(
        intensities=np.empty(
            shape=(count,) + template.intensities.layout.shape,
            dtype=template.intensities.dtype,
        ),
        ranges=np.empty(
            shape=(count,) + template.ranges.layout.shape,
            dtype=template.ranges.dtype,
        ),
        normals=np.empty(
            shape=(count,) + template.normals.layout.shape,
            dtype=template.normals.dtype,
        ),
    )


def allocate_bundle_storage(
    group: H5Database.Group, template: ImageBundleTemplate, count: int
) -> ImageBundleStorage:
    """Allocate datasets for the given template and count."""

    intensities = group.create_dataset(
        "intensities",
        shape=(count,) + template.intensities.layout.shape,
        dtype=template.intensities.dtype,
    )
    ranges = group.create_dataset(
        "ranges",
        shape=(count,) + template.ranges.layout.shape,
        dtype=template.ranges.dtype,
    )
    normals = group.create_dataset(
        "normals",
        shape=(count,) + template.normals.layout.shape,
        dtype=template.normals.dtype,
    )

    return ImageBundleStorage(intensities, ranges, normals)
