"""Module for exporting stereo geometry, including rectification results, range maps, and normal maps."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import tqdm


from mynd.camera import CameraID, CameraCalibration
from mynd.image import Image, ImageLoader
from mynd.io import write_image

from mynd.geometry import HitnetModel, remap_image_pixels
from mynd.geometry import (
    StereoRectificationResult,
    compute_stereo_rectification,
)
from mynd.geometry import StereoGeometry, compute_stereo_geometry

from mynd.utils.containers import Pair
from mynd.utils.result import Ok, Err, Result


@dataclass
class ExportStereoTask:
    """Facade class for stereo export task."""

    @dataclass
    class Config:
        """Class representing a task configuration."""

        range_directory: Path
        normal_directory: Path
        disparity_estimator: (
            HitnetModel  # TODO: Add disparity estimator interface
        )
        calibrations: Pair[CameraCalibration]
        camera_pairs: list[Pair[CameraID]]
        image_loaders: list[Pair[ImageLoader]]

        image_filter: Optional = None
        disparity_filter: Optional = None

    @dataclass
    class Result:
        """Class representing a task result."""

        write_errors: list[str] = field(default_factory=list)


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

    rectification: StereoRectificationResult = compute_stereo_rectification(
        config.calibrations
    )

    for camera_pair in tqdm.tqdm(
        config.camera_pairs, desc="Estimating stereo geometry..."
    ):

        loaders: Pair[ImageLoader] = Pair(
            config.image_loaders.get(camera_pair.first),
            config.image_loaders.get(camera_pair.second),
        )

        assert loaders.first is not None, "invalid first image loader"
        assert loaders.second is not None, "invalid second image loader"

        images: Pair[Image] = Pair(
            first=loaders.first(),
            second=loaders.second(),
        )

        assert images.first is not None, "invalid first image"
        assert images.second is not None, "invalid second image"

        # Create paths
        filepaths: list[Path] = {
            "first_ranges": config.range_directory
            / f"{camera_pair.first.label}.tiff",
            "second_ranges": config.range_directory
            / f"{camera_pair.second.label}.tiff",
            "first_normals": config.normal_directory
            / f"{camera_pair.first.label}.tiff",
            "second_normals": config.normal_directory
            / f"{camera_pair.second.label}.tiff",
        }

        # Check if stereo geometry has already been exported
        if all([path.exists() for key, path in filepaths.items()]):
            continue

        stereo_geometry: StereoGeometry = compute_stereo_geometry(
            rectification=rectification,
            matcher=config.disparity_estimator,
            images=images,
            image_filter=config.image_filter,
            disparity_filter=config.disparity_filter,
        )

        # Remapped range maps to original camera model
        remapped_range_maps: Pair[np.ndarray] = Pair(
            first=remap_image_pixels(
                stereo_geometry.range_maps.first,
                rectification.inverse_pixel_maps.first,
            ),
            second=remap_image_pixels(
                stereo_geometry.range_maps.second,
                rectification.inverse_pixel_maps.second,
            ),
        )

        # Remapped normal maps to original camera model
        remapped_normal_maps: Pair[np.ndarray] = Pair(
            first=remap_image_pixels(
                stereo_geometry.normal_maps.first,
                rectification.inverse_pixel_maps.first,
            ),
            second=remap_image_pixels(
                stereo_geometry.normal_maps.second,
                rectification.inverse_pixel_maps.second,
            ),
        )

        # TODO: Add visualization
        # TODO: Cast geometry values

        results: list = [
            write_image(
                uri=f"{config.range_directory}/{camera_pair.first.label}.tiff",
                image=remapped_range_maps.first.to_array().astype(np.float16),
            ),
            write_image(
                uri=f"{config.range_directory}/{camera_pair.second.label}.tiff",
                image=remapped_range_maps.second.to_array().astype(np.float16),
            ),
            write_image(
                uri=f"{config.normal_directory}/{camera_pair.first.label}.tiff",
                image=remapped_normal_maps.first.to_array().astype(np.float16),
            ),
            write_image(
                uri=f"{config.normal_directory}/{camera_pair.second.label}.tiff",
                image=remapped_normal_maps.second.to_array().astype(np.float16),
            ),
        ]

        results: list = list()

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
