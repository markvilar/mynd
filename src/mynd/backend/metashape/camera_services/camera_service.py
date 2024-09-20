"""Module for camera services for the Metashape backend."""

from typing import Any, Callable

import Metashape as ms

from mynd.api import (
    GroupID,
    CameraAttributeGroup,
    CameraReferenceGroup,
    StereoCameraGroup,
)
from mynd.utils.result import Ok, Err, Result

from .camera_helpers import get_camera_attribute_group, get_stereo_group
from .reference_helpers import (
    get_estimated_camera_reference_group,
    get_prior_camera_reference_group,
)
from ..context import get_document


CallbackResult = Result[Any, str]


def get_document_and_dispatch(
    callback: Callable[[ms.Document], CallbackResult]
) -> CallbackResult:
    """Retrieves the document from the backend and dispatches to the success callback."""
    get_document_result: Result[ms.Document, str] = get_document()

    match get_document_result:
        case Ok(document):
            return callback(document)
        case Err(message):
            return Err(message)


CameraAttributeResponse = dict[GroupID, CameraAttributeGroup]


def get_camera_attributes() -> Result[CameraAttributeResponse, str]:
    """Retrieves camera attributes from the Metashape backend, including keys,
    labels, image label, sensor keys, and master keys."""
    return get_document_and_dispatch(camera_attribute_callback)


def camera_attribute_callback(
    document: ms.Document,
) -> Result[CameraAttributeResponse, str]:
    """Callback that retrieves camera identifiers from a document."""
    response_data: CameraAttributeResponse = {
        GroupID(chunk.key, chunk.label): get_camera_attribute_group(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)


CameraReferenceResponse = dict[GroupID, CameraReferenceGroup]


def get_estimated_camera_references() -> Result[CameraReferenceResponse, str]:
    """Gets the estimated camera references for each chunk if a document is loaded.
    Returns an error with a message if no document is loaded."""
    return get_document_and_dispatch(estimated_camera_reference_callback)


def estimated_camera_reference_callback(
    document: ms.Document,
) -> Result[CameraReferenceResponse, str]:
    """Callback that retrieves camera references from a document."""
    response_data: CameraReferenceResponse = {
        GroupID(chunk.key, chunk.label): get_estimated_camera_reference_group(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)


def get_prior_camera_references() -> Result[CameraReferenceResponse, str]:
    """Gets the estimated camera references for each chunk if a document is loaded.
    Returns an error with a message if no document is loaded."""
    return get_document_and_dispatch(prior_camera_reference_callback)


def prior_camera_reference_callback(
    document: ms.Document,
) -> Result[CameraReferenceResponse, str]:
    """Callback that retrieves prior camera references from a document."""
    response_data: CameraReferenceResponse = {
        GroupID(chunk.key, chunk.label): get_prior_camera_reference_group(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)


StereoCameraResponse = dict[GroupID, StereoCameraGroup]


def get_stereo_cameras() -> Result[StereoCameraResponse, str]:
    """Gets stereo cameras from each chunk in a document. If an error with a
    message if no document is loaded."""
    return get_document_and_dispatch(stereo_camera_callback)


def stereo_camera_callback(document: ms.Document) -> Result[StereoCameraResponse, str]:
    """Callback that retrieves stereo cameras from a document"""
    response_data: dict[int, list[StereoCameraGroup]] = {
        GroupID(chunk.key, chunk.label): get_stereo_group(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)
