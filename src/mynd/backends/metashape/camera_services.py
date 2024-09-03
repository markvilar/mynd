"""Module for camera services for the Metashape backend."""

import Metashape

from ...api.camera import StereoCollection
from ...api.identifier import Identifier
from ...utils.result import Ok, Err, Result

from .camera_helpers import get_stereo_collections
from .context import get_document


ResponseData = dict[int, StereoCollection]


def request_stereo_data() -> Result[ResponseData, str]:
    """Retrieves the document from the backend context, and extracts the stereo data
    from the document chunks."""

    result: Result[Metashape.Document, str] = get_document()

    match result:
        case Ok(document):
            return on_stereo_data_request(document)
        case Err(error):
            return Err(error)
        case _:
            raise NotImplementedError

    raise NotImplementedError("request_stereo_data is not implemented")


def on_stereo_data_request(document: Metashape.Document) -> Result[ResponseData, str]:
    """Handles stereo data requests."""

    data: dict[int, list[StereoCollection]] = {
        Identifier(chunk.key, chunk.label): get_stereo_collections(chunk)
        for chunk in document.chunks
    }

    return Ok(data)
