"""Module for the Metashape backend context."""

from contextvars import ContextVar
from pathlib import Path
from typing import Any

import Metashape

from result import Ok, Err, Result

from benthoscan.utils.log import logger

from .project import (
    load_document,
    save_document,
    METASHAPE_DOCUMENT_EXTENSIONS,
)


METASHAPE_DOCUMENT = "document"


_context = ContextVar("metashape_context", default={})


_backend_data: dict[str, Any] = {}
_backend_data[METASHAPE_DOCUMENT] = None


def log_internal_data() -> None:
    """Logs the internal data of the backend."""
    logger.info(_backend_data)


def load_project(path: str | Path) -> Result[str, str]:
    """Loads an existing project from file."""

    path: Path = Path(path)

    if _backend_data[METASHAPE_DOCUMENT] is not None:
        return Err("backend already has a loaded project")

    if path.suffix not in METASHAPE_DOCUMENT_EXTENSIONS:
        return Err(f"path is not a metashape project: {path}")

    result: Result[Metashape.Document, str] = load_document(path)

    match result:
        case Ok(document):
            _backend_data[METASHAPE_DOCUMENT] = document
            return Ok(f"loaded document {path} successfully")
        case Err(message):
            return Err(message)
        case _:
            return Err(f"unknown error during document loading: {path}")


def save_project(path: str | Path) -> Result[Path, str]:
    """Saves an existing project to file."""

    if _backend_data[METASHAPE_DOCUMENT] is None:
        return Err("backend does not have a loaded project")

    if path.suffix not in METASHAPE_DOCUMENT_EXTENSIONS:
        return Err(f"path is not a metashape project: {path}")

    return save_document(_backend_data[METASHAPE_DOCUMENT], path)
