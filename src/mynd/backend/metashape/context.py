"""Module for the Metashape backend context."""

from pathlib import Path
from typing import Any, Callable

import Metashape as ms

from mynd.collections import GroupID
from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result

from .project import (
    load_document,
    save_document,
    VALID_DOCUMENT_EXTENSIONS,
)


DOCUMENT_PATH_KEY = "url"
DOCUMENT_KEY = "document"


_backend_data: dict[str, Any] = {}
_backend_data[DOCUMENT_PATH_KEY] = None
_backend_data[DOCUMENT_KEY] = None


def get_document() -> Result[ms.Document, str]:
    """Request the document from the backend."""

    if not _backend_data.get(DOCUMENT_KEY):
        return Err("no loaded document in backend")

    document: ms.Document = _backend_data.get(DOCUMENT_KEY)
    return Ok(document)


def retrieve_document_and_dispatch(
    callback: Callable[[ms.Document], Result[Any, str]], **kwargs
) -> Result[Any, str]:
    """Retrieves a document and dispatches it to the callback."""
    get_document_result: Result[ms.Document, str] = get_document()

    match get_document_result:
        case Ok(document):
            return Ok(callback(document, **kwargs))
        case Err(message):
            return Err(message)
        case _:
            raise NotImplementedError(
                "invalid match case in retrieve_document_and_dispatch"
            )


def log_internal_data() -> None:
    """Logs the internal data of the backend."""
    logger.info(_backend_data)


def get_project_url() -> Result[str | Path, str]:
    """Returns the URL of the currently loaded project."""
    return retrieve_document_and_dispatch(_get_document_path)


def _get_document_path(document: ms.Document) -> str:
    """Returns the path of the given document."""
    return document.path


def get_group_identifiers() -> Result[list[GroupID], str]:
    """Returns the group identifiers in the currently loaded project."""
    return retrieve_document_and_dispatch(_get_chunk_identifiers)


def _get_chunk_identifiers(
    document: ms.Document,
) -> list[GroupID]:
    """Returns the chunk key and label as identifiers."""
    return [
        GroupID(key=chunk.key, label=chunk.label) for chunk in document.chunks
    ]


def loaded_project() -> bool:
    """Returns true if a project is loaded, and false if it is not."""
    return _backend_data.get(DOCUMENT_KEY) is not None


def load_project(path: str | Path) -> Result[str, str]:
    """Loads an existing project from file."""

    path: Path = Path(path)

    if _backend_data[DOCUMENT_KEY] is not None:
        return Err("backend already has a loaded project")

    if path.suffix not in VALID_DOCUMENT_EXTENSIONS:
        return Err(f"path is not a metashape project: {path}")

    result: Result[ms.Document, str] = load_document(path)

    match result:
        case Ok(document):
            _backend_data[DOCUMENT_PATH_KEY] = path
            _backend_data[DOCUMENT_KEY] = document
            return Ok(f"loaded document {path} successfully")
        case Err(message):
            return Err(message)
        case _:
            return Err(f"unknown error during document loading: {path}")


def save_project(path: str | Path) -> Result[Path, str]:
    """Saves an existing project to file."""

    if _backend_data[DOCUMENT_KEY] is None:
        return Err("backend does not have a loaded project")

    if path.suffix not in VALID_DOCUMENT_EXTENSIONS:
        return Err(f"path is not a metashape project: {path}")

    return save_document(_backend_data[DOCUMENT_KEY], path)
