"""Module for the Metashape backend context."""

from pathlib import Path
from typing import Any

import Metashape as ms

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


def log_internal_data() -> None:
    """Logs the internal data of the backend."""
    logger.info(_backend_data)


def get_project() -> Result[str | Path, str]:
    """Returns the currently loaded project."""
    url: str | Path = _backend_data.get(DOCUMENT_PATH_KEY)
    if url is None:
        return Err("no loaded backend project")
    return Ok(url)


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
