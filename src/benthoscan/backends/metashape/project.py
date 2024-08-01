""" Metashape document functions. """

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias, Callable

import Metashape

from result import Ok, Err, Result


METASHAPE_DOCUMENT_EXTENSIONS = [".psz", ".psx"]


def create_document() -> Metashape.Document:
    """Create a metashape document."""
    return Metashape.Document()


def load_document(path: Path) -> Result[Metashape.Document, str]:
    """Loads the document from the given path."""
    if not path.exists():
        return Err(f"path does not exist: {path}")
    if not path.is_file():
        return Err(f"document path is not a file: {path}")
    if not path.suffix in METASHAPE_DOCUMENT_EXTENSIONS:
        return Err(f"invalid document extension: {path}")

    document: Metashape.Document = create_document()
    try:
        document.open(str(path))
    except IOError as error:
        return Err(error)
    return Ok(document)


def save_document(document: Metashape.Document, path: Path = None) -> Result[Path, str]:
    """Saves the document to the given path."""
    if not path:
        return save_document_to_path(document, Path(document.path))
    else:
        return save_document_to_path(document, path)


def save_document_to_path(document: Metashape.Document, path: Path) -> Result[Path, str]:
    """Saves the document to the given path."""
    if not path.suffix in METASHAPE_DOCUMENT_EXTENSIONS:
        return Err(f"invalid document extension: {path}")

    try:
        document.save(str(path))
    except OSError as error:
        return Err(str(error))
    return Ok(path)


def create_chunk(document: Metashape.Document, label: str = None) -> Metashape.Chunk:
    """Creates a chunk for the given document."""
    chunk: Metashape.Chunk = document.addChunk()
    if label:
        chunk.label = label
    return chunk
