"""Module for estimating stereo geometry, i.e. estimating ranges and normals from image pairs."""

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from mynd.camera import CameraCalibration
from mynd.image import Image, PixelFormat

from mynd.utils.containers import Pair

from .image_transformations import PixelMap, remap_image_pixels
from .range_maps import compute_range_from_disparity, compute_normals_from_range
from .stereo_matcher import StereoMatcher
from .stereo_rectification import (
    StereoRectificationResult,
    rectify_image_pair,
)


@dataclass
class StereoGeometry:
    """Class representing a stereo geometry."""

    rectification: StereoRectificationResult
    raw_images: Pair[Image]
    rectified_images: Pair[Image]
    disparities: Pair[np.ndarray]
    range_maps: Optional[Pair[Image]] = None
    normal_maps: Optional[Pair[Image]] = None


ImageFilter = Callable[[Image], Image]
DisparityFilter = Callable[[np.ndarray], np.ndarray]


def compute_stereo_geometry(
    rectification: StereoRectificationResult,
    matcher: StereoMatcher,
    images: Pair[Image],
    image_filter: Optional[ImageFilter] = None,
    disparity_filter: Optional[DisparityFilter] = None,
) -> StereoGeometry:
    """Computes range and normal maps for a rectified stereo setup, a disparity matcher, and
    a pair of images."""

    rectified_calibrations: Pair[CameraCalibration] = (
        rectification.rectified_calibrations
    )

    # Rectify images
    rectified_images: Pair[Image] = rectify_image_pair(images, rectification)

    if image_filter:
        rectified_images: Pair[Image] = Pair(
            first=image_filter(rectified_images.first),
            second=image_filter(rectified_images.second),
        )

    # Estimate disparity from rectified images
    disparity_maps: Pair[np.ndarray] = matcher(
        left=rectified_images.first,
        right=rectified_images.second,
    )

    if disparity_filter:
        disparity_maps: Pair[np.ndarray] = Pair(
            first=disparity_filter(disparity_maps.first),
            second=disparity_filter(disparity_maps.second),
        )

    baseline: float = rectified_calibrations.second.baseline

    # Estimate range from disparity
    range_maps: Pair[np.ndarray] = Pair(
        first=compute_range_from_disparity(
            disparity=disparity_maps.first,
            baseline=baseline,
            focal_length=rectified_calibrations.first.focal_length,
        ),
        second=compute_range_from_disparity(
            disparity=disparity_maps.second,
            baseline=baseline,
            focal_length=rectified_calibrations.second.focal_length,
        ),
    )

    # Estimate normals from range maps
    normal_maps: Pair[np.ndarray] = Pair(
        first=compute_normals_from_range(
            range_map=range_maps.first,
            camera_matrix=rectified_calibrations.first.camera_matrix,
            flipped=True,
        ),
        second=compute_normals_from_range(
            range_map=range_maps.second,
            camera_matrix=rectified_calibrations.second.camera_matrix,
            flipped=True,
        ),
    )

    # Insert the range and normal maps into image containers
    range_maps: Pair[Image] = Pair(
        first=Image.from_array(range_maps.first, PixelFormat.X),
        second=Image.from_array(range_maps.second, PixelFormat.X),
    )
    normal_maps: Pair[Image] = Pair(
        first=Image.from_array(normal_maps.first, PixelFormat.XYZ),
        second=Image.from_array(normal_maps.second, PixelFormat.XYZ),
    )

    stereo_geometry: StereoGeometry = StereoGeometry(
        rectification=rectification,
        raw_images=images,
        rectified_images=rectified_images,
        disparities=disparity_maps,
        range_maps=range_maps,
        normal_maps=normal_maps,
    )

    return stereo_geometry


def distort_stereo_geometry(
    geometry: StereoGeometry,
) -> tuple[Pair[Image], ...]:
    """Distorts range and normal maps for the given stereo geometry."""

    inverse_pixel_maps: Pair[PixelMap] = (
        geometry.rectification.inverse_pixel_maps
    )

    distorted_ranges: Pair[Image] = Pair(
        first=remap_image_pixels(
            image=geometry.range_maps.first,
            pixel_map=inverse_pixel_maps.first,
        ),
        second=remap_image_pixels(
            image=geometry.range_maps.second,
            pixel_map=inverse_pixel_maps.second,
        ),
    )

    distorted_normals: Pair[Image] = Pair(
        first=remap_image_pixels(
            image=geometry.normal_maps.first,
            pixel_map=inverse_pixel_maps.first,
        ),
        second=remap_image_pixels(
            image=geometry.normal_maps.second,
            pixel_map=inverse_pixel_maps.second,
        ),
    )

    return distorted_ranges, distorted_normals
