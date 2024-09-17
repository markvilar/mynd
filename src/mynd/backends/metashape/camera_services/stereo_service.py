"""Module with stereo related services."""

import Metashape as ms

from mynd.api import Identifier, StereoBundle
from mynd.utils.result import Ok, Result

from .camera_helpers import get_stereo_bundles
from ..context import get_document


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
