"""Module for metadata services."""

from typing import Any

import Metashape as ms

from mynd.camera import CameraID
from mynd.collections import CameraGroup

from mynd.utils.literals import literal_primitive
from mynd.utils.result import Ok, Result

from .common import retrieve_chunk_and_dispatch


GroupID = CameraGroup.Identifier
CameraMetadata = dict[CameraID, dict]


def update_camera_metadata(
    identifier: GroupID, metadata: dict[str, dict]
) -> Result[str, str]:
    """Updates the metadata for cameras in a Metashape chunk."""
    return retrieve_chunk_and_dispatch(
        identifier, callback=update_camera_metadata_callback, metadata=metadata
    )


def update_camera_metadata_callback(
    chunk: ms.Chunk, identifier: GroupID, metadata: dict[str, dict]
) -> Result[dict, str]:
    """Callback that updates the camera metadata in a Metashape chunk."""

    updated_cameras: dict[str, dict] = dict()
    for camera in chunk.cameras:
        if camera.label not in metadata:
            continue

        fields: dict = metadata.get(camera.label)

        for field, value in fields.items():
            # NOTE: Metashape only allows string values in camera metadata
            camera.meta[str(field)] = str(value)
        updated_cameras[camera.label] = fields

    return Ok(updated_cameras)


def get_camera_metadata(identifier: GroupID) -> Result[CameraMetadata, str]:
    """Gets camera metadata from the target group."""
    return retrieve_chunk_and_dispatch(identifier, get_camera_metadata_callback)


def get_camera_metadata_callback(
    chunk: ms.Chunk, identifier: GroupID
) -> Result[CameraMetadata, str]:
    """Callback that retrieves camera metadata from a chunk."""

    metadata: dict[CameraID, dict] = dict()
    for camera in chunk.cameras:

        camera_identifier: CameraID = CameraID(camera.key, camera.label)

        fields: dict[str, Any] = {
            key: literal_primitive(value) for key, value in camera.meta.items()
        }

        metadata[camera_identifier] = fields

    return Ok(metadata)
