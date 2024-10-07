"""Module for exporting stereo geometry, including rectification results, range maps, and normal maps."""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import tqdm

from ..camera import CameraCalibration
from ..image import Image, PixelFormat, ImageLoader
from ..containers import Pair

from ..geometry import HitnetConfig, compute_disparity
from ..geometry import remap_image_pixels
from ..geometry import (
    RectificationResult,
    compute_stereo_rectification,
    rectify_image_pair,
)
from ..geometry import compute_range_from_disparity, compute_normals_from_range

from ..io import write_image
from ..utils.result import Ok, Err, Result


@dataclass
class ExportStereoTask:
    """Facade class for stereo export task."""

    @dataclass
    class Config:
        """Class representing a task configuration."""

        range_directory: Path
        normal_directory: Path
        model: HitnetConfig  # TODO: Add disparity estimator interface
        calibrations: Pair[CameraCalibration]
        image_loaders: list[Pair[ImageLoader]]

    @dataclass
    class Result:
        """Class representing a task result."""

        write_errors: list[str] = field(default_factory=list)


def compute_stereo_geometry(
    rectification: RectificationResult,
    matcher: HitnetConfig,
    images: Pair[Image],
) -> tuple[Pair[Image], Pair[Image]]:
    """Computes range and normal maps for a rectified stereo setup, a disparity matcher, and
    a pair of images."""

    rectified_calibrations: Pair[CameraCalibration] = (
        rectification.rectified_calibrations
    )

    # Rectify images
    rectified_images: Pair[Image] = rectify_image_pair(images, rectification)

    # Estimate disparity from rectified images
    disparity_maps: Pair[np.ndarray] = compute_disparity(
        matcher,
        left=rectified_images.first,
        right=rectified_images.second,
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

    return range_maps, normal_maps


def export_stereo_geometry(
    config: ExportStereoTask.Config,
) -> Result[ExportStereoTask.Result, str]:
    """Rectifies a stereo camera calibration, loads images, and computes range and normal maps.
    Exports the range and normal maps to image files."""

    if not config.range_directory.exists():
        return Err(f"range directory does not exist: {config.range_directory}")
    if not config.normal_directory.exists():
        return Err(
            f"normal directory does not exist: {config.normal_directory}"
        )

    task_result: ExportStereoTask.Result = ExportStereoTask.Result()

    rectification: RectificationResult = compute_stereo_rectification(
        config.calibrations
    )

    for loaders in tqdm.tqdm(config.image_loaders, desc="Loading images..."):
        images: Pair[Image] = Pair(
            first=loaders.first(), second=loaders.second()
        )

        # Create paths
        filepaths: list[Path] = {
            "first_ranges": config.range_directory
            / f"{images.first.label}.tiff",
            "second_ranges": config.range_directory
            / f"{images.second.label}.tiff",
            "first_normals": config.normal_directory
            / f"{images.first.label}.tiff",
            "second_normals": config.normal_directory
            / f"{images.second.label}.tiff",
        }

        if all([path.exists() for key, path in filepaths.items()]):
            continue

        range_maps: Pair[Image]
        normal_maps: Pair[Image]
        range_maps, normal_maps = compute_stereo_geometry(
            rectification, config.model, images
        )

        # Remapped range maps to original camera model
        remapped_range_maps: Pair[np.ndarray] = Pair(
            first=remap_image_pixels(
                range_maps.first, rectification.inverse_pixel_maps.first
            ),
            second=remap_image_pixels(
                range_maps.second, rectification.inverse_pixel_maps.second
            ),
        )

        # Remapped normal maps to original camera model
        remapped_normal_maps: Pair[np.ndarray] = Pair(
            first=remap_image_pixels(
                normal_maps.first, rectification.inverse_pixel_maps.first
            ),
            second=remap_image_pixels(
                normal_maps.second, rectification.inverse_pixel_maps.second
            ),
        )

        # Write range and normal maps to file
        results: list = [
            write_image(
                uri=filepaths.get("first_ranges"),
                image=remapped_range_maps.first.to_array().astype(np.float16),
            ),
            write_image(
                uri=filepaths.get("second_ranges"),
                image=remapped_range_maps.second.to_array().astype(np.float16),
            ),
            write_image(
                uri=filepaths.get("first_normals"),
                image=remapped_normal_maps.first.to_array().astype(np.float16),
            ),
            write_image(
                uri=filepaths.get("second_normals"),
                image=remapped_normal_maps.second.to_array().astype(np.float16),
            ),
        ]

        for result in results:
            if result.is_err():
                task_result.write_errors.append(result.err())

    return Ok(task_result)


def invoke_stereo_export_task(
    config: ExportStereoTask.Config,
) -> Result[ExportStereoTask.Result, str]:
    """Invoke a stereo export task."""

    # TODO: Add config validation

    # Compute stereo range and normal maps and export
    return export_stereo_geometry(config)
