"""Module for executing project setup tasks."""

from pathlib import Path
from typing import Any

import polars as pl

from ...camera import Sensor, Frame
from ...camera import create_sensor, read_frames_from_dataframe
from ...containers import Registry, create_file_registry_from_directory
from ...io import read_config, read_data_frame
from ...spatial import SpatialReference, build_references_from_dataframe

from ...utils.log import logger
from ...utils.result import Ok, Err, Result

# TODO: Remove - package no longer exists
from ...project import CameraGroupData, ProjectData

from .config_types import CameraGroupConfig, ProjectConfig


def get_frames_invalid_sensors(camera_group: CameraGroupData) -> list[Frame]:
    """Validates the camera group by removing frames with invalid sensors."""

    group_sensors: list[Sensor] = camera_group.sensors
    invalid_frames: list[Frame] = list()

    for frame in camera_group.frames:
        missing_sensors: list[bool] = [
            sensor not in group_sensors for sensor in frame.sensors
        ]

        if any(missing_sensors):
            invalid_frames.append(frame)

    return invalid_frames


def get_frames_invalid_keys(camera_group: CameraGroupData) -> list[Frame]:
    """Validates the camera group by removing frames with invalid labels, i.e.
    images that are not in the image registry."""

    registered_keys: list[str] = camera_group.images.keys
    invalid_frames: list[Frame] = list()

    for frame in camera_group.frames:
        missing_keys: list[bool] = [
            image_key not in registered_keys for image_key in frame.image_keys
        ]

        if any(missing_keys):
            invalid_frames.append(frame)

    return invalid_frames


def remove_invalid_camera_frames(camera_group: CameraGroupData):
    """Validates the camera group by checking that every frame has sensor images."""

    invalid_sensor_frames: list[Frame] = get_frames_invalid_sensors(
        camera_group
    )
    invalid_key_frames: list[Frame] = get_frames_invalid_keys(camera_group)

    for frame in invalid_sensor_frames:
        logger.warning(f"frame with invalid sensors: {frame.key}")
        camera_group.frames.remove(frame)

    for frame in invalid_key_frames:
        logger.warning(f"frame with invalid image keys: {frame.key}")
        camera_group.frames.remove(frame)


def configure_camera_group(config: CameraGroupConfig) -> CameraGroupData:
    """Prepares a chunk for initialization by registering images, and
    loading camera labels, camera sensors, and references."""

    camera_data: pl.DataFrame = read_data_frame(config.camera_data).unwrap()
    data_config: dict = read_config(config.camera_config).unwrap()

    for key in ["camera", "reference"]:
        if key not in data_config:
            return Err(f"missing data configuration group: '{key}'")

    # Extract the different entries from the configuration
    reference_config: dict[str, Any] = data_config.get("reference")
    camera_config: dict[str, Any] = data_config.get("camera")

    sensors: list[dict] = camera_config.get("sensors")
    frame_maps: list[dict] = camera_config.get("frames")

    sensors: list[Sensor] = [create_sensor(config) for config in sensors]

    frames: list[Frame] = read_frames_from_dataframe(
        dataframe=camera_data,
        mappings=frame_maps,
        sensors=sensors,
    ).unwrap()

    # Create cameras from a dataframe under the assumption that we only have one group,
    # i.e. one setup (mono, stereo, etc.) for all the cameras

    references: list[SpatialReference] = build_references_from_dataframe(
        camera_data,
        reference_config["column_maps"],
        reference_config["constants"],
    ).unwrap()

    reference_registry: Registry[str, SpatialReference] = Registry[
        str, SpatialReference
    ]()

    for reference in references:
        reference_registry.insert(reference.identifier.label, reference)

    # TODO: Move file extensions to config
    image_registry: Registry[str, Path] = create_file_registry_from_directory(
        config.image_directory,
        extensions=[".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    return CameraGroupData(
        config.name,
        sensors=sensors,
        frames=frames,
        images=image_registry,
        references=reference_registry,
    )


def execute_project_setup(config: ProjectConfig) -> Result[ProjectData, str]:
    """Executes a project setup by setting up the project data based on the given configuration."""

    camera_groups: list[CameraGroupData] = [
        configure_camera_group(chunk) for chunk in config.camera_groups
    ]

    # Remove invalid frames of the camera group - invalid sensors and missing images
    for camera_group in camera_groups:
        remove_invalid_camera_frames(camera_group)

    project_data: ProjectData = ProjectData(
        document_options=config.document_options,
        camera_groups=camera_groups,
    )

    return Ok(project_data)
