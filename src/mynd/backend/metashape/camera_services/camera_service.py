"""Module for camera services for the Metashape backend."""

from typing import Any, Callable

import Metashape as ms

from mynd.api import (
    GroupID,
    CameraIndexGroup,
    CameraReferenceGroup,
    StereoGroup,
)
from mynd.utils.result import Ok, Err, Result

from .camera_helpers import get_index_group, get_stereo_group
from .reference_helpers import get_reference_group
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


CameraIndexResponse = dict[GroupID, CameraIndexGroup]


def get_camera_indices() -> Result[CameraIndexResponse, str]:
    """Retrieves camera data from the Metashape backend, including indices, labels,
    and prior and aligned poses."""
    return get_document_and_dispatch(camera_index_callback)


def camera_index_callback(
    document: ms.Document,
) -> Result[CameraIndexResponse, str]:
    """Callback that retrieves camera identifiers from a document."""
    response_data: CameraIndexResponse = {
        GroupID(chunk.key, chunk.label): get_index_group(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)


CameraReferenceResponse = dict[GroupID, CameraReferenceGroup]


def get_camera_references() -> Result[CameraReferenceResponse, str]:
    """Gets camera references for each chunk if a document is loaded. Returns an
    error with a message if no document is loaded."""
    return get_document_and_dispatch(camera_reference_callback)


def camera_reference_callback(
    document: ms.Document,
) -> Result[CameraReferenceResponse, str]:
    """Callback that retrieves camera references from a document."""
    response_data: CameraReferenceResponse = {
        GroupID(chunk.key, chunk.label): get_reference_group(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)


StereoCameraResponse = dict[GroupID, StereoGroup]


def get_stereo_cameras() -> Result[StereoCameraResponse, str]:
    """Gets stereo cameras from each chunk in a document. If an error with a
    message if no document is loaded."""
    return get_document_and_dispatch(stereo_camera_callback)


def stereo_camera_callback(document: ms.Document) -> Result[StereoCameraResponse, str]:
    """Callback that retrieves stereo cameras from a document"""
    response_data: dict[int, list[StereoGroup]] = {
        GroupID(chunk.key, chunk.label): get_stereo_group(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)
