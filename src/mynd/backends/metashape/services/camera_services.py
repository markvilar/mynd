"""Module for camera services for the ms.backend."""

import Metashape as ms

from ....api.camera import CameraBundle, StereoBundle
from ....api.identifier import Identifier
from ....utils.result import Ok, Result

from ..camera.camera_helpers import get_stereo_bundles, get_camera_bundle
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


StereoResponseData = dict[Identifier, StereoBundle]


def request_stereo_bundles() -> Result[StereoResponseData, str]:
    """Retrieves the document from the backend context, and extracts the stereo data
    from the document chunks."""

    get_document_result: Result[ms.Document, str] = get_document()

    if get_document_result.is_err():
        return get_document_result

    document: ms.Document = get_document_result.ok()

    data: dict[int, list[StereoBundle]] = {
        Identifier(chunk.key, chunk.label): get_stereo_bundles(chunk)
        for chunk in document.chunks
    }

    return Ok(data)
