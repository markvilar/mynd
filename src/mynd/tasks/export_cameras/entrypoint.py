"""Module for exporting camera data including keys, labels, images, and references."""

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Optional

from ...camera import Camera, Sensor
from ...collections import CameraGroup
from ...io.hdf import H5Database, create_file_database, load_file_database
from ...utils.log import logger
from ...utils.result import Result

# Import handlers for subtasks
from .camera_export_handler import handle_camera_export
from .image_export_handler import handle_image_export


CameraID = Camera.Identifier
SensorID = Sensor.Identifier

IMAGE_STORAGE_GROUP: str = "images"


def export_camera_group(
    destination: Path,
    cameras: CameraGroup,
    images: Optional[Mapping[str, Iterable[Path]]] = None,
) -> Result[str, str]:
    """Entrypoint for exporting camera groups. Initializes data storage and
    dispatches to relevant subtasks."""

    log_task_header(cameras, images)

    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    if cameras.identifier.label in database:
        main_group: H5Database.Group = database.get(cameras.identifier.label)
    else:
        main_group: H5Database.Group = database.create_group(
            cameras.identifier.label
        ).unwrap()

    # Export camera attributes and references
    handle_camera_export(main_group, cameras, error_callback=on_error)

    # In order to export images, we check that an image storage group is not
    # already present in the database, and that bundle loaders are provided
    if IMAGE_STORAGE_GROUP in main_group:
        logger.warning(
            f"'{IMAGE_STORAGE_GROUP}' is already in storage group {main_group.name}"
        )
        pass
    elif images:
        handle_image_export(
            main_group,
            cameras.attributes,
            images,
            error_callback=on_error,
        )


def log_task_header(
    cameras: CameraGroup, images: Optional[Mapping[str, Iterable[Path]]]
) -> None:
    """Logs a header with summary statistics before exporting cameras."""

    if images is not None:
        image_count: int = sum([len(items) for items in images.values()])
    else:
        image_count: int = 0

    group_label: str = cameras.identifier.label
    camera_count: int = len(cameras.attributes.identifiers)
    estimated_count: int = len(cameras.estimated_references.identifiers)
    prior_count: int = len(cameras.prior_references.identifiers)

    logger.info("")
    logger.info(f"Exporting camera group: {group_label}")
    logger.info(f"Camera attributes:      {camera_count}")
    logger.info(f"Estimated references:   {estimated_count}")
    logger.info(f"Prior references:       {prior_count}")
    logger.info(f"Images:                 {image_count}")
    logger.info("")


def on_error(message: str) -> None:
    """Callback that is called on an error result."""
    logger.error(message)
