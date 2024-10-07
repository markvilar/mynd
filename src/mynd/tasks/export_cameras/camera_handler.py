"""Module for handling export of cameras."""

from typing import Callable

from ...collections import CameraGroup

from ...io.hdf import H5Database
from ...io.hdf import (
    insert_camera_attributes_into,
    insert_camera_references_into,
)

from ...utils.log import logger
from ...utils.result import Ok, Err, Result


StorageGroup = H5Database.Group
ErrorCallback = Callable[[str], None]

CAMERA_STORAGE_GROUPS: list[str] = [
    "cameras",
    "references/aligned",
    "references/priors",
]


def handle_camera_export(
    storage: StorageGroup,
    camera_group: CameraGroup,
    error_callback: ErrorCallback = lambda message: None,
) -> None:
    """Handles exporting of camera groups."""

    existing_groups: list[str] = [
        group for group in CAMERA_STORAGE_GROUPS if group in storage
    ]

    assert (
        not existing_groups
    ), f"camera storage groups already exist: {*existing_groups,}"

    if camera_group.attributes:
        result: Result[None, str] = insert_camera_attributes_into(
            storage.create_group("cameras"),
            camera_group.attributes,
        )

        match result:
            case Ok(None):
                logger.info("successfully wrote camera attributes")
            case Err(message):
                error_callback(message)

    if camera_group.estimated_references:
        result: Result[None, str] = insert_camera_references_into(
            storage.create_group("references/aligned"),
            camera_group.estimated_references,
        )

        match result:
            case Ok(None):
                logger.info("successfully wrote aligned references")
            case Err(message):
                error_callback(message)

    if camera_group.prior_references:
        result: Result[None, str] = insert_camera_references_into(
            storage.create_group("references/priors"),
            camera_group.prior_references,
        )

        match result:
            case Ok(None):
                logger.info("successfully wrote prior references")
            case Err(message):
                error_callback(message)
