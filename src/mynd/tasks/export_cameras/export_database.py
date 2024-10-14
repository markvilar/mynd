"""Module for export handlers."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, TypeAlias

from mynd.camera import CameraID, Metadata
from mynd.collections import CameraGroup, SensorImages
from mynd.image import ImageCompositeLoader

from mynd.io.h5 import H5Database, load_file_database, create_file_database
from mynd.io.h5 import (
    insert_camera_attributes_into,
    insert_camera_references_into,
    insert_image_composites_into,
    insert_camera_identifiers_into,
)

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


StorageGroup = H5Database.Group
ErrorCallback = Callable[[str], None]

CameraMetadata: TypeAlias = Mapping[CameraID, Metadata]
ImageCompositeLoaders: TypeAlias = Mapping[CameraID, ImageCompositeLoader]


H5Group: TypeAlias = H5Database.Group


CAMERA_STORAGE_GROUPS: list[str] = [
    "cameras",
    "references/aligned",
    "references/priors",
]


CAMERA_STORAGE_NAME: str = "cameras"
IMAGE_STORAGE_GROUP: str = "images"
METADATA_STORAGE_GROUP: str = "metadata"


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
    metadata: Optional[CameraMetadata] = None,
    error_callback: Callable = None,
) -> Result[None, str]:
    """Handles exporting cameras and images to a database."""

    context: StorageContext = initialize_storage(destination)

    export_tasks: list[ExportTask] = configure_export_tasks(
        context,
        camera_group,
        image_groups,
        metadata,
    )

    for task in export_tasks:
        task.handler(
            task.storage,
            **task.arguments,
            result_callback=task.result_callback,
            error_callback=task.error_callback,
        )

    context.handle.visit(logger.info)


def initialize_storage(destination: Path) -> StorageContext:
    """Initializes the storage context by loading or creating a file database."""

    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    return StorageContext(database)


def configure_export_tasks(
    context: StorageContext,
    cameras: CameraGroup,
    image_groups: Optional[list[SensorImages]] = None,
    metadata: Optional[CameraMetadata] = None,
) -> list[ExportTask]:
    """Creates export configurations by loading a database and creating storage groups."""

    base_name: str = cameras.group_identifier.label
    base_group: H5Group = context.handle.create_group(base_name).unwrap()

    export_tasks: list[ExportTask] = list()

    export_tasks.append(
        configure_camera_export(
            base_group,
            CAMERA_STORAGE_NAME,
            cameras,
        )
    )

    if image_groups is not None:
        for image_group in image_groups:

            storage_name: str = (
                f"{IMAGE_STORAGE_GROUP}/{image_group.sensor.label}"
            )

            export_tasks.append(
                configure_image_export(
                    base=base_group,
                    storage_name=storage_name,
                    images=image_group,
                )
            )

    if metadata is not None:
        export_tasks.append(
            configure_metadata_export(
                base=base_group,
                storage_name=METADATA_STORAGE_GROUP,
                metadata=metadata,
            )
        )

    return export_tasks


def configure_camera_export(
    base: H5Group,
    storage_name: str,
    cameras: CameraGroup,
) -> ExportTask:
    """Creates a camera export configuration."""
    storage_group: H5Group = base.create_group(storage_name)
    return ExportTask(
        arguments={"cameras": cameras},
        storage=storage_group,
        handler=handle_camera_export,
        error_callback=None,
    )


def configure_image_export(
    base: H5Group, storage_name: str, images: SensorImages
) -> ExportTask:
    """Creates an image export configuration."""
    storage_group: H5Group = base.create_group(storage_name)
    return ExportTask(
        arguments={"images": images},
        storage=storage_group,
        handler=handle_image_export,
        error_callback=None,
    )


def configure_metadata_export(
    base: H5Group,
    storage_name: str,
    metadata: CameraMetadata,
) -> ExportTask:
    """Creates a metadata export configuration."""
    storage_group: H5Group = base.create_group(storage_name)
    return ExportTask(
        arguments={"metadata": metadata},
        storage=storage_group,
        handler=handle_metadata_export,
        error_callback=None,
    )


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
                logger.trace("wrote camera attributes!")
            case Err(message):
                error_callback(message)

    if cameras.estimated_references:
        result: Result[None, str] = insert_camera_references_into(
            storage.create_group("references/aligned"),
            cameras.estimated_references,
        )

        match result:
            case Ok(None):
                logger.trace("wrote aligned references!")
            case Err(message):
                error_callback(message)

    if cameras.prior_references:
        result: Result[None, str] = insert_camera_references_into(
            storage.create_group("references/priors"),
            cameras.prior_references,
        )

        match result:
            case Ok(None):
                logger.trace("wrote prior references!")
            case Err(message):
                error_callback(message)


def handle_image_export(
    storage: H5Database.Group,
    images: SensorImages,
    result_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
) -> None:
    """Handles exporting of image groups."""

    write_result: Result[None, str] = insert_sensor_images_into(
        storage=storage, sensor_images=images
    )

    match write_result:
        case Ok(None):
            logger.info("Successfully inserted sensor images!")
        case Err(message):
            if error_callback:
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
