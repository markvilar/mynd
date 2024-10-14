"""Module for export handlers."""

from collections.abc import Mapping
from typing import Callable, Optional, TypeAlias

from mynd.camera import CameraID, Metadata
from mynd.collections import CameraGroup, SensorImages
from mynd.image import ImageCompositeLoader

from mynd.io.h5 import H5Database
from mynd.io.h5 import (
    insert_camera_attributes_into,
    insert_camera_references_into,
    insert_image_bundles_into,
    insert_camera_identifiers_into,
    insert_labels_into,
)

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


StorageGroup = H5Database.Group
ErrorCallback = Callable[[str], None]

CameraMetadata: TypeAlias = Mapping[CameraID, Metadata]
ImageCompositeLoaders: TypeAlias = Mapping[CameraID, ImageCompositeLoader]


CAMERA_STORAGE_GROUPS: list[str] = [
    "cameras",
    "references/aligned",
    "references/priors",
]


def handle_camera_export(
    storage: StorageGroup,
    cameras: CameraGroup,
    result_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
) -> None:
    """Handles exporting of camera groups."""

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
                logger.info("successfully wrote camera attributes")
            case Err(message):
                error_callback(message)

    if cameras.estimated_references:
        result: Result[None, str] = insert_camera_references_into(
            storage.create_group("references/aligned"),
            cameras.estimated_references,
        )

        match result:
            case Ok(None):
                logger.info("successfully wrote aligned references")
            case Err(message):
                error_callback(message)

    if cameras.prior_references:
        result: Result[None, str] = insert_camera_references_into(
            storage.create_group("references/priors"),
            cameras.prior_references,
        )

        match result:
            case Ok(None):
                logger.info("successfully wrote prior references!")
            case Err(message):
                error_callback(message)


def handle_image_export(
    storage: H5Database.Group,
    images: SensorImages,
    result_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
) -> None:
    """Handles exporting of image groups."""

    write_result: Result[None, str] = insert_sensor_images_into(storage=storage, sensor_images=images)

    match write_result:
        case Ok(None):
            logger.info("Successfully inserted sensor images!")
        case Err(message):
            error_callback(message)


def handle_metadata_export(
    storage: H5Database.Group, 
    metadata: Mapping[CameraID, dict],
    result_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
) -> Result[None, str]:
    """Handles exporting of camera metadata."""

    # TODO: Figure out how to write metadata to H5 files

    raise NotImplementedError("handle_metadata_export is not implemented")


def insert_sensor_images_into(
    storage: H5Database.Group,
    sensor_images: SensorImages,
) -> Result[None, str]:
    """Insert a group images into a storage group."""

    # We create lists of data members since they are order preserving
    cameras: list[CameraID] = sorted(
        sensor_images.cameras, key=lambda item: item.key
    )
    labels: list[str] = [sensor_images.labels.get(camera) for camera in cameras]
    loaders: list[ImageCompositeLoader] = [
        sensor_images.loaders.get(camera) for camera in cameras
    ]

    invalid_labels: list[bool] = [label is None for label in labels]
    invalid_loaders: list[bool] = [loader is None for loader in loaders]

    if any(invalid_labels):
        return Err(f"missing {sum(invalid_labels)} labels for cameras")
    if any(invalid_loaders):
        return Err(f"missing {sum(invalid_loaders)} loaders for cameras")

    storage.attrs["sensor_key"] = sensor_images.sensor.key
    storage.attrs["sensor_label"] = sensor_images.sensor.label

    # Insert the sensor image components into the storage
    insert_results: list[Result[None, str]] = [
        insert_camera_identifiers_into(storage, cameras),
        insert_labels_into(storage, labels),
        insert_image_bundles_into(storage, loaders),
    ]

    for result in insert_results:
        if result.is_err():
            return result

    return Ok(None)
