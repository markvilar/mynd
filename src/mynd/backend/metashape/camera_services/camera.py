"""Module for camera services for the Metashape backend."""

import Metashape as ms

from mynd.camera import Camera, CameraID
from mynd.collections import CameraGroup
from mynd.utils.result import Ok, Result

from .. import helpers as helpers
from .common import retrieve_chunk_and_dispatch


GroupID = CameraGroup.Identifier


def retrieve_camera_group(identifier: GroupID) -> Result[CameraGroup, str]:
    """Retrieves a camera group from the Metashape backend."""
    return retrieve_chunk_and_dispatch(
        identifier, retrieve_camera_group_callback
    )


def retrieve_camera_group_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup, str]:
    """Callback that retrieves a camera group from a document."""

    attributes: CameraGroup.Attributes = helpers.get_camera_attribute_group(
        chunk
    )
    est_references: CameraGroup.References = (
        helpers.get_camera_reference_estimates(chunk)
    )
    pri_references: CameraGroup.References = (
        helpers.get_camera_reference_priors(chunk)
    )
    metadata: CameraGroup.Metadata = helpers.get_camera_metadata(chunk)

    return Ok(
        CameraGroup(
            group_identifier=identifier,
            attributes=attributes,
            reference_estimates=est_references,
            reference_priors=pri_references,
            metadata=metadata,
        )
    )


def retrieve_camera_attributes(
    identifier: GroupID,
) -> Result[CameraGroup.Attributes, str]:
    """Retrieves camera attributes from the Metashape backend, including keys,
    labels, image label, sensor keys, and master keys."""
    return retrieve_chunk_and_dispatch(
        identifier, retrieve_camera_attributes_callback
    )


def retrieve_camera_attributes_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup.Attributes, str]:
    """Callback that retrieves camera identifiers from a document."""
    attributes: CameraGroup.Attributes = helpers.get_camera_attribute_group(
        chunk
    )
    return Ok(attributes)


def retrieve_camera_metadata(
    identifier: GroupID,
) -> Result[CameraGroup.Metadata, str]:
    """Gets camera metadata from the target group."""
    return retrieve_chunk_and_dispatch(
        identifier, retrieve_camera_metadata_callback
    )


def retrieve_camera_metadata_callback(
    chunk: ms.Chunk, identifier: GroupID
) -> Result[CameraGroup.Metadata, str]:
    """Callback that retrieves camera metadata from a chunk."""
    metadata: CameraGroup.Metadata = helpers.get_camera_metadata(chunk)
    return Ok(metadata)


def retrieve_camera_reference_estimates(
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Retrieves the estimated camera references for each chunk if a document
    is loaded. Returns an error with a message if no document is loaded."""
    return retrieve_chunk_and_dispatch(
        identifier, retrieve_reference_estimates_callback
    )


def retrieve_reference_estimates_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Callback that retrieves camera references from a document."""
    references: CameraGroup.References = helpers.get_camera_reference_estimates(
        chunk
    )
    return Ok(references)


def retrieve_camera_reference_priors(
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Gets the estimated camera references for each chunk if a document is loaded.
    Returns an error with a message if no document is loaded."""
    return retrieve_chunk_and_dispatch(
        identifier, retrieve_reference_priors_callback
    )


def retrieve_reference_priors_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Callback that retrieves prior camera references from a document."""
    references: CameraGroup.References = helpers.get_camera_reference_priors(
        chunk
    )
    return Ok(references)


def update_camera_metadata(
    identifier: GroupID, metadata: dict[str, Camera.Metadata]
) -> Result[str, str]:
    """Updates the metadata for cameras in a Metashape chunk."""
    return retrieve_chunk_and_dispatch(
        identifier, callback=update_camera_metadata_callback, metadata=metadata
    )


def update_camera_metadata_callback(
    chunk: ms.Chunk, identifier: GroupID, metadata: dict[str, Camera.Metadata]
) -> Result[None, str]:
    """Callback that updates the camera metadata in a Metashape chunk."""
    helpers.update_camera_metadata(chunk, metadata)
    return Ok(None)
