"""Module for camera services for the Metashape backend."""

import Metashape as ms

from mynd.collections import CameraGroup
from mynd.utils.result import Ok, Result

from ..helpers.camera import get_camera_attribute_group
from ..helpers.reference import (
    get_camera_reference_estimates,
    get_camera_reference_priors,
)
from .common import retrieve_chunk_and_dispatch


GroupID = CameraGroup.Identifier


def get_camera_attributes(
    identifier: GroupID,
) -> Result[CameraGroup.Attributes, str]:
    """Retrieves camera attributes from the Metashape backend, including keys,
    labels, image label, sensor keys, and master keys."""
    return retrieve_chunk_and_dispatch(identifier, camera_attribute_callback)


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
    return retrieve_chunk_and_dispatch(
        identifier, estimated_camera_reference_callback
    )


def estimated_camera_reference_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Callback that retrieves camera references from a document."""
    references: CameraGroup.References = get_camera_reference_estimates(chunk)
    return Ok(references)


def get_prior_camera_references(
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Gets the estimated camera references for each chunk if a document is loaded.
    Returns an error with a message if no document is loaded."""
    return retrieve_chunk_and_dispatch(
        identifier, prior_camera_reference_callback
    )


def prior_camera_reference_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[CameraGroup.References, str]:
    """Callback that retrieves prior camera references from a document."""
    references: CameraGroup.References = get_camera_reference_priors(chunk)
    return Ok(references)
