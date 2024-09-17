"""Module for camera services for the ms.backend."""

import Metashape as ms

from mynd.api import Identifier, CameraBundle
from mynd.utils.result import Ok, Result

from .camera_helpers import get_camera_bundle
from ..context import get_document


CameraResponseData = dict[Identifier, CameraBundle]


def request_camera_bundles() -> Result[CameraResponseData, str]:
    """Retrieves camera data from the Metashape backend, including indices, labels,
    and prior and aligned poses."""

    get_document_result: Result[ms.Document, str] = get_document()

    if get_document_result.is_err():
        return get_document_result

    document: ms.Document = get_document_result.ok()

    response_data: CameraResponseData = dict()
    for chunk in document.chunks:
        camera_bundle: CameraBundle = get_camera_bundle(chunk)
        identifier: Identifier = Identifier(chunk.key, chunk.label)
        response_data[identifier] = camera_bundle

    return Ok(response_data)
