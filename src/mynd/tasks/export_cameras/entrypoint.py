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
from .image_export_handler import handle_image_export


CameraID = Camera.Identifier
SensorID = Sensor.Identifier

IMAGE_STORAGE_GROUP: str = "images"


def export_camera_group(
    destination: Path,
    camera_group: CameraGroup,
    images: Optional[Mapping[str, Iterable[Path]]] = None,
) -> Result[str, str]:
    """Entrypoint for exporting camera groups. Initializes data storage and
    dispatches to relevant subtasks."""

    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    logger.info(f"Exporting camera group:   {camera_group.identifier.label}")
    logger.info(f"  Camera attributes:      {len(camera_group.attributes.identifiers)}")
    logger.info(
        f"  Estimated references:   {len(camera_group.estimated_references.identifiers)}"
    )
    logger.info(
        f"  Prior references:       {len(camera_group.prior_references.identifiers)}"
    )
    logger.info(
        f"  Images:                 {sum([len(items) for items in images.values()])}"
    )

    if camera_group.identifier.label in database:
        main_group: H5Database.Group = database.get(camera_group.identifier.label)
    else:
        main_group: H5Database.Group = database.create_group(
            camera_group.identifier.label
        ).unwrap()

    # TODO: Export camera attributes
    # TODO: Export estimated camera references
    # TODO: Export prior camera references

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
            camera_group.attributes,
            images,
            error_callback=on_error,
        )


def on_error(message: str) -> None:
    """Callback that is called on an error result."""
    logger.error(message)
