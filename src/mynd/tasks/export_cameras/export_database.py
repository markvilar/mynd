"""Module for export handlers."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, TypeAlias

from mynd.camera import CameraID
from mynd.collections import CameraGroup, SensorImages
from mynd.image import ImageCompositeLoader

from mynd.geometry import StereoRectificationResult, compute_stereo_rectification

from mynd.io.h5 import H5Database, load_file_database, create_file_database
from mynd.io.h5 import (
    insert_camera_identifiers_into,
    insert_camera_attributes_into,
    insert_camera_references_into,
    insert_camera_metadata_into,
    insert_image_composites_into,
)

from mynd.io.h5 import (
    insert_sensor_identifier_into,
    insert_sensor_into,
    insert_calibration_into,
    insert_stereo_rectification_into,
)

from mynd.utils.containers import Pair
from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


StorageGroup = H5Database.Group
ErrorCallback = Callable[[str], None]


ImageCompositeLoaders: TypeAlias = Mapping[CameraID, ImageCompositeLoader]
H5Group: TypeAlias = H5Database.Group


CAMERA_STORAGE_GROUPS: list[str] = [
    "cameras",
    "references/aligned",
    "references/priors",
]


CAMERA_STORAGE_NAME: str = "cameras"
IMAGE_STORAGE_GROUP: str = "images"


@dataclass
class StorageContext:
    """Class representing a storage context."""

    handle: H5Database


@dataclass
class ExportTask:
    """Class representing an export task."""

    arguments: dict[str, Any]
    storage: H5Group
    handler: Callable
    result_callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None


def export_cameras_database(
    destination: Path,
    camera_group: CameraGroup,
    image_groups: Optional[list[SensorImages]] = None,
    error_callback: Callable = None,
) -> Result[None, str]:
    """Handles exporting cameras and images to a database."""

    context: StorageContext = initialize_storage(destination)

    # Create base storage group
    base_name: str = camera_group.group_identifier.label
    base_group: H5Group = context.handle.create_group(base_name).unwrap()

    handle_camera_export(base_group, camera_group)

    if image_groups is not None:
        for image_group in image_groups:
            handle_image_export(base_group, images=image_group)

    context.handle.visit(logger.info)


def initialize_storage(destination: Path) -> StorageContext:
    """Initializes the storage context by loading or creating a file database."""

    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    return StorageContext(database)


def handle_camera_export(
    base: StorageGroup,
    cameras: CameraGroup,
    result_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
) -> None:
    """Handles exporting of camera groups."""

    storage: H5Group = base.create_group(CAMERA_STORAGE_NAME)

    existing_groups: list[str] = [
        group for group in CAMERA_STORAGE_GROUPS if group in storage
    ]

    assert (
        not existing_groups
    ), f"camera storage groups already exist: {*existing_groups,}"

    if cameras.attributes:
        result: Result[None, str] = insert_camera_attributes_into(
            storage.create_group("attributes"),
            cameras.attributes,
        )

        match result:
            case Ok(None):
                logger.trace("wrote camera attributes!")
            case Err(message):
                error_callback(message)

    if cameras.reference_estimates:
        result: Result[None, str] = insert_camera_references_into(
            storage.create_group("references/aligned"),
            cameras.reference_estimates,
        )

        match result:
            case Ok(None):
                logger.trace("wrote aligned references!")
            case Err(message):
                error_callback(message)

    if cameras.reference_priors:
        result: Result[None, str] = insert_camera_references_into(
            storage.create_group("references/priors"),
            cameras.reference_priors,
        )

        match result:
            case Ok(None):
                logger.trace("wrote prior references!")
            case Err(message):
                error_callback(message)

    if cameras.metadata:
        result: Result[None, str] = insert_camera_metadata_into(
            storage.create_group("metadata"),
            cameras.metadata,
        )

        match result:
            case Ok(None):
                logger.trace("wrote camera metadata!")
            case Err(message):
                error_callback(message)

    if cameras.attributes:
        for sensor in cameras.attributes.sensors:
            result: Result[None, str] = insert_sensor_into(
                storage.create_group(f"sensors/{sensor.identifier.label}"),
                sensor,
            )

            match result:
                case Ok(None):
                    logger.trace("wrote camera sensor!")
                case Err(message):
                    error_callback(message)

    if cameras.attributes:
        stereo_pairs: list[Pair[Sensor]] = cameras.attributes.stereo_sensors

        assert len(stereo_pairs) == 1, "multiple stereo pairs is not handled"

        for stereo_pair in stereo_pairs:
            calibrations: Pair[CameraCalibration] = Pair(
                stereo_pair.first.calibration,
                stereo_pair.second.calibration,
            )

            rectification: StereoRectificationResult = compute_stereo_rectification(calibrations)

            result: Result[None, str] = insert_sensor_identifier_into(
                storage.create_group(f"stereo/sensors/{stereo_pair.first.identifier.label}"),
                stereo_pair.first.identifier,
            )

            result: Result[None, str] = insert_sensor_identifier_into(
                storage.create_group(f"stereo/sensors/{stereo_pair.second.identifier.label}"),
                stereo_pair.second.identifier,
            )

            insert_stereo_rectification_into(
                storage.create_group(f"stereo/rectification"),
                rectification,
            )


def handle_image_export(
    base: H5Database.Group,
    images: SensorImages,
    result_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
) -> None:
    """Handles exporting of image groups."""

    storage_name: str = (f"{IMAGE_STORAGE_GROUP}/{images.sensor.label}")
    storage: H5Group = base.create_group(storage_name)

    write_result: Result[None, str] = insert_sensor_images_into(
        storage=storage, sensor_images=images
    )

    match write_result:
        case Ok(None):
            logger.info("Successfully inserted sensor images!")
        case Err(message):
            if error_callback:
                error_callback(message)


def insert_sensor_images_into(
    storage: H5Database.Group,
    sensor_images: SensorImages,
) -> Result[None, str]:
    """Insert a group images into a storage group."""

    # We create lists of data members since they are order preserving
    cameras: list[CameraID] = sorted(
        sensor_images.cameras, key=lambda item: item.key
    )
    loaders: list[ImageCompositeLoader] = [
        sensor_images.loaders.get(camera) for camera in cameras
    ]

    invalid_loaders: list[bool] = [loader is None for loader in loaders]

    if any(invalid_loaders):
        return Err(f"missing {sum(invalid_loaders)} loaders for cameras")

    storage.attrs["sensor_key"] = sensor_images.sensor.key
    storage.attrs["sensor_label"] = sensor_images.sensor.label

    # Insert the sensor image components into the storage
    insert_results: list[Result[None, str]] = [
        insert_camera_identifiers_into(storage, cameras),
        insert_image_composites_into(storage, loaders),
    ]

    for result in insert_results:
        if result.is_err():
            return result

    return Ok(None)
