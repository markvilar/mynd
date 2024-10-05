"""Module for camera services for the Metashape backend."""

from typing import Any, Callable

import Metashape as ms

from mynd.collections import CameraGroup, StereoCameraGroup
from mynd.utils.result import Ok, Err, Result

from .camera_helpers import (
    get_camera_attribute_group,
    get_stereo_group,
)
from .reference_helpers import (
    get_estimated_camera_reference_group,
    get_prior_camera_reference_group,
)
from ..context import get_document


GroupID = CameraGroup.Identifier


CallbackResult = Result[Any, str]
TargetCallback = Callable[[GroupID, ms.Chunk], CallbackResult]


def get_chunk_and_dispatch(
    identifier: GroupID,
    callback: TargetCallback,
    **kwargs,
) -> CallbackResult:
    """Retrieves the document from the backend and dispatches to the success callback."""

    match get_document():
        case Ok(document):
            chunks: dict[GroupID, ms.Chunk] = get_chunk_identifiers(document)
            if identifier in chunks:
                return callback(chunks.get(identifier), identifier, **kwargs)
            else:
                return Err(f"invalid group identifier: {identifier}")
        case Err(message):
            return Err(message)


def get_chunk_identifiers(document: ms.Document) -> dict[GroupID, ms.Chunk]:
    """Returns a mapping from group identifiers to Metashape chunks."""
    return {GroupID(chunk.key, chunk.label): chunk for chunk in document.chunks}


def get_camera_attributes(
    identifier: GroupID,
) -> Result[CameraGroup.Attributes, str]:
    """Retrieves camera attributes from the Metashape backend, including keys,
    labels, image label, sensor keys, and master keys."""
    return get_chunk_and_dispatch(identifier, camera_attribute_callback)


def camera_attribute_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup.Attributes, str]:
    """Callback that retrieves camera identifiers from a document."""
    attributes: CameraGroup.Attributes = get_camera_attribute_group(chunk)
    return Ok(attributes)


def get_estimated_camera_references(
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Gets the estimated camera references for each chunk if a document is loaded.
    Returns an error with a message if no document is loaded."""
    return get_chunk_and_dispatch(
        identifier, estimated_camera_reference_callback
    )


def estimated_camera_reference_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Callback that retrieves camera references from a document."""
    references: CameraGroup.References = get_estimated_camera_reference_group(
        chunk
    )
    return Ok(references)


def get_prior_camera_references(
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Gets the estimated camera references for each chunk if a document is loaded.
    Returns an error with a message if no document is loaded."""
    return get_chunk_and_dispatch(identifier, prior_camera_reference_callback)


def prior_camera_reference_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Callback that retrieves prior camera references from a document."""
    references: CameraGroup.References = get_prior_camera_reference_group(chunk)
    return Ok(references)


def get_stereo_cameras(identifier: GroupID) -> Result[StereoCameraGroup, str]:
    """Gets stereo cameras from each chunk in a document. If an error with a
    message if no document is loaded."""
    return get_chunk_and_dispatch(identifier, stereo_camera_callback)


def stereo_camera_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[StereoCameraGroup, str]:
    """Callback that retrieves stereo cameras from a document"""
    stereo_cameras: list[StereoCameraGroup] = get_stereo_group(chunk)
    return Ok(stereo_cameras)


def update_camera_metadata(
    identifier: GroupID, metadata: dict[str, dict]
) -> Result[str, str]:
    """Updates the metadata for cameras in a Metashape chunk."""
    return get_chunk_and_dispatch(
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
