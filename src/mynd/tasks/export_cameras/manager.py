"""Module for managing export of camera attributes, metadata, and images."""

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import NamedTuple, Optional

from ...camera import Camera, Sensor
from ...collections import CameraGroup
from ...io.hdf import H5Database, create_file_database, load_file_database
from ...utils.log import logger
from ...utils.result import Ok, Result

# Import handlers for subtasks
from .camera_handler import handle_camera_export
from .image_handler import handle_image_export


CameraID = Camera.Identifier
SensorID = Sensor.Identifier


ResultType = None
ErrorType = str


METADATA_STORAGE_GROUP: str = "metadata"
IMAGE_STORAGE_GROUP: str = "images"


class StorageGroups(NamedTuple):
    """Class representing camera export storage groups."""

    base: H5Database.Group
    cameras: H5Database.Group
    images: H5Database.Group
    metadata: H5Database.Group


Metadata = dict[str, str | int | float | bool]


def manage_camera_group_export(
    destination: Path,
    cameras: CameraGroup,
    images: Optional[Mapping[str, Iterable[Path]]] = None,
    metadata: Optional[Mapping[CameraID, Metadata]] = None,
) -> Result[ResultType, ErrorType]:
    """Entrypoint for exporting camera groups. Initializes data storage and
    dispatches to relevant subtasks."""

    log_task_header(cameras, images)

    storage: H5Database.Group = retrieve_storage_group(
        destination=destination, name=cameras.identifier.label
    )

    # Export camera attributes and references
    handle_camera_export(storage, cameras, error_callback=on_error)

    # In order to export images, we check that an image storage group is not
    # already present in the database, and that bundle loaders are provided
    if IMAGE_STORAGE_GROUP in storage:
        logger.warning(
            f"'{IMAGE_STORAGE_GROUP}' is already in storage group {storage.name}"
        )
        pass
    elif images:
        handle_image_export(
            storage,
            cameras.attributes,
            images,
            error_callback=on_error,
        )

    return Ok(None)


def retrieve_storage_group(destination: Path, name: str) -> H5Database.Group:
    """Prepare storage group."""
    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    if name in database:
        storage_group: H5Database.Group = database.get(name)
    else:
        storage_group: H5Database.Group = database.create_group(name).unwrap()

    return storage_group


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
