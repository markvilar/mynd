"""Module for exporting stereo geometry, including rectification results, range
maps, and normal maps."""

import os

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import numpy as np
import tqdm

from mynd.camera import CameraID
from mynd.collections import StereoCameraGroup

from mynd.geometry import StereoMatcher, create_hitnet_matcher
from mynd.geometry import (
    StereoGeometry,
    compute_stereo_geometry,
    distort_stereo_geometry,
)
from mynd.geometry import (
    StereoRectificationResult,
    compute_stereo_rectification,
)

from mynd.image import Image, ImageLoader
from mynd.io import write_image

from mynd.visualization import (
    StereoWindows,
    create_stereo_windows,
    render_stereo_geometry,
    destroy_all_windows,
    wait_key_input,
    create_stereo_geometry_color_image,
)

from mynd.utils.containers import Pair
from mynd.utils.key_codes import KeyCode
from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


@dataclass
class ExportStereoGeometryConfig:
    """Class representing a configuration for exporting stereo geometry."""

    @dataclass
    class Directories:
        """Class representing export paths."""

        base: Path
        ranges: Path
        normals: Path
        samples: Path | None = None

    # TODO: Add stereo estimation configuration
    @dataclass
    class Processors:
        """Class representing stereo geometry processors."""

        disparity_estimator: StereoMatcher
        image_filter: object | None = None
        disparity_filter: object | None = None

    directories: Directories
    processors: Processors


Config: TypeAlias = ExportStereoGeometryConfig


def export_stereo_geometry(
    stereo_group: StereoCameraGroup,
    destination: Path,
    matcher: Path,
    visualize: bool,
    save_samples: bool,
) -> Result[None, str]:
    """Invoke a stereo export task."""

    logger.info(f"Stereo group:     {stereo_group.group_identifier}")
    logger.info(f"Destination:      {destination}")
    logger.info(f"Matcher:          {matcher}")
    logger.info(f"Visualize:        {visualize}")
    logger.info(f"Save samples:     {save_samples}")

    # TODO: Create configuration
    directories: Config.Directories = prepare_export_directories(
        destination, stereo_group, save_samples
    )
    processors: Config.Processors = prepare_stereo_processors(matcher)

    config: Config = Config(directories, processors)

    logger.info("Directories:")
    logger.info(f" - Base:      {config.directories.base}")
    logger.info(f" - Ranges:    {config.directories.ranges}")
    logger.info(f" - Normals:   {config.directories.normals}")
    logger.info(f" - Samples:   {config.directories.samples}")
    logger.info("")

    rectification: StereoRectificationResult = compute_stereo_rectification(
        stereo_group.calibrations
    )

    if visualize:
        windows: StereoWindows = create_stereo_windows()
    else:
        windows = None

    EXPORT_SAMPLE_EVERY: int = 50
    for index, camera_pair in tqdm.tqdm(
        enumerate(stereo_group.camera_pairs),
        desc="Estimating stereo geometry...",
    ):

        loaders: Pair[ImageLoader] = Pair(
            stereo_group.image_loaders.get(camera_pair.first),
            stereo_group.image_loaders.get(camera_pair.second),
        )

        assert loaders.first is not None, "invalid first image loader"
        assert loaders.second is not None, "invalid second image loader"

        images: Pair[Image] = Pair(
            first=loaders.first(),
            second=loaders.second(),
        )

        assert images.first is not None, "invalid first image"
        assert images.second is not None, "invalid second image"

        geometry: StereoGeometry = compute_stereo_geometry(
            rectification=rectification,
            images=images,
            matcher=config.processors.disparity_estimator,
            image_filter=config.processors.image_filter,
            disparity_filter=config.processors.disparity_filter,
        )

        # TODO: Add option to distort or leave undistorted
        ranges: Pair[Image]
        normals: Pair[Image]
        ranges, normals = distort_stereo_geometry(geometry)

        if directories.samples and index % EXPORT_SAMPLE_EVERY == 0:
            combined_image: Image = create_stereo_geometry_color_image(
                geometry.raw_images, ranges, normals
            )
            export_stereo_geometry_sample(
                directories=directories,
                camera_pair=camera_pair,
                image=combined_image,
            )

        # Write stereo geometry
        results: list[Result] = write_stereo_geometry(
            directories=config.directories,
            camera_pair=camera_pair,
            ranges=ranges,
            normals=normals,
        )

        for result in results:
            if result.is_err():
                logger.error(result.err())

        if windows:
            # Visualize stereo geometry mapped back into the distorted image frame
            render_stereo_geometry(windows, geometry, distort=True)

            match wait_key_input(100):
                case KeyCode.ESC:
                    logger.info("Quitting...")
                    destroy_all_windows()
                    return
                case KeyCode.SPACE:
                    continue
                case _:
                    continue


def prepare_export_directories(
    destination: Path,
    stereo_group: StereoCameraGroup,
    save_samples: bool,
) -> Config.Directories:
    """Prepares export paths by creating directories relative to the
    destination directory."""

    name: str = stereo_group.group_identifier.label

    base_directory: Path = destination
    range_directory: Path = base_directory / f"{name}_ranges"
    normal_directory: Path = base_directory / f"{name}_normals"

    if save_samples:
        sample_directory: Path = base_directory / f"{name}_samples"
    else:
        sample_directory = None

    directories: Config.Directories = Config.Directories(
        base_directory,
        range_directory,
        normal_directory,
        sample_directory,
    )

    if not directories.base.exists():
        os.mkdir(str(directories.base))
    if not directories.ranges.exists():
        os.mkdir(str(directories.ranges))
    if not directories.normals.exists():
        os.mkdir(str(directories.normals))
    if directories.samples is not None and not directories.samples.exists():
        os.mkdir(str(directories.samples))

    return directories


def prepare_stereo_processors(matcher: Path) -> Config.Processors:
    """Prepares stereo processors."""

    stereo_matcher: StereoMatcher = create_hitnet_matcher(matcher)

    processors: Config.Processors = Config.Processors(
        disparity_estimator=stereo_matcher,
        image_filter=None,
        disparity_filter=None,
    )

    return processors


def write_stereo_geometry(
    directories: Config.Directories,
    camera_pair: Pair[CameraID],
    ranges: Pair[Image],
    normals: Pair[Image],
) -> None:
    """Writes stereo range and normals map to file."""

    filenames: Pair[str] = Pair(
        first=f"{camera_pair.first.label}.tiff",
        second=f"{camera_pair.second.label}.tiff",
    )

    results: list[Result] = [
        write_image(
            directories.ranges / filenames.first,
            ranges.first.to_array().astype(np.float16),
        ),
        write_image(
            directories.ranges / filenames.second,
            ranges.second.to_array().astype(np.float16),
        ),
        write_image(
            directories.normals / filenames.first,
            normals.first.to_array().astype(np.float16),
        ),
        write_image(
            directories.normals / filenames.second,
            normals.second.to_array().astype(np.float16),
        ),
    ]

    return results


def export_stereo_geometry_sample(
    directories: Config.Directories,
    camera_pair: Pair[CameraID],
    image: Image,
) -> None:
    """Exports a palette of stereo images."""

    write_result: Result = write_image(
        directories.samples / f"{camera_pair.first.label}_sample.png", image
    )

    match write_result:
        case Ok(None):
            pass
        case Err(message):
            logger.error(f"failed to write stereo sample: {message}")
