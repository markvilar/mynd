"""Module with common service functionality."""

from typing import Any, Callable, Optional

import Metashape as ms

from mynd.collections import CameraGroup
from mynd.utils.result import Ok, Err, Result

from ..context import get_document


GroupID = CameraGroup.Identifier
CallbackResult = Result[Any, str]
TargetCallback = Callable[[ms.Chunk, GroupID, ...], CallbackResult]


def retrieve_chunk_and_dispatch(
    identifier: GroupID,
    callback: TargetCallback,
    **kwargs,
) -> CallbackResult:
    """Retrieves the document from the backend and dispatches to the success callback."""

    match get_document():
        case Ok(document):
            chunk: Optional[ms.Chunk] = get_chunk(document, identifier)
            if chunk is not None:
                return callback(chunk, identifier, **kwargs)
            else:
                return Err(f"invalid group identifier: {identifier}")
        case Err(message):
            return Err(message)


def get_chunk(document: ms.Document, identifier: GroupID) -> Optional[ms.Chunk]:
    """Gets a chunk from a document if the identifier matches, and none otherwise."""
    chunks: dict[GroupID, ms.Chunk] = get_chunk_identifiers(document)
    return chunks.get(identifier)


def get_chunk_identifiers(document: ms.Document) -> dict[GroupID, ms.Chunk]:
    """Returns a mapping from group identifiers to Metashape chunks."""
    return {GroupID(chunk.key, chunk.label): chunk for chunk in document.chunks}
