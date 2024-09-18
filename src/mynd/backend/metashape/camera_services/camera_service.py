"""Module for camera services for the Metashape backend."""

from typing import Any, Callable

import Metashape as ms

from mynd.api import (
    Identifier,
    CameraCollection,
    CameraReferenceCollection,
    StereoCollection,
)
from mynd.utils.result import Ok, Err, Result

from .camera_helpers import get_camera_collection, get_stereo_collection
from .reference_helpers import get_reference_collection
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


CameraIdentifierResponse = dict[Identifier, CameraCollection]


def get_cameras() -> Result[CameraIdentifierResponse, str]:
    """Retrieves camera data from the Metashape backend, including indices, labels,
    and prior and aligned poses."""
    return get_document_and_dispatch(camera_identifier_callback)


def camera_identifier_callback(
    document: ms.Document,
) -> Result[CameraIdentifierResponse, str]:
    """Callback that retrieves camera identifiers from a document."""
    response_data: CameraIdentifierResponse = {
        Identifier(chunk.key, chunk.label): get_camera_collection(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)


CameraReferenceResponse = dict[Identifier, CameraReferenceCollection]


def get_camera_references() -> Result[CameraReferenceResponse, str]:
    """Gets camera references for each chunk if a document is loaded. Returns an
    error with a message if no document is loaded."""
    return get_document_and_dispatch(camera_reference_callback)


def camera_reference_callback(
    document: ms.Document,
) -> Result[CameraReferenceResponse, str]:
    """Callback that retrieves camera references from a document."""
    response_data: CameraReferenceResponse = {
        Identifier(chunk.key, chunk.label): get_reference_collection(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)


StereoCameraResponse = dict[Identifier, StereoCollection]


def get_stereo_cameras() -> Result[StereoCameraResponse, str]:
    """Gets stereo cameras from each chunk in a document. If an error with a
    message if no document is loaded."""
    return get_document_and_dispatch(stereo_camera_callback)


def stereo_camera_callback(document: ms.Document) -> Result[StereoCameraResponse, str]:
    """Callback that retrieves stereo cameras from a document"""
    response_data: dict[int, list[StereoCollection]] = {
        Identifier(chunk.key, chunk.label): get_stereo_collection(chunk)
        for chunk in document.chunks
    }
    return Ok(response_data)
