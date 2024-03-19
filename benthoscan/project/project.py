""" Metashape document functions. """

from pathlib import Path
from typing import TypeAlias

import Metashape

from result import Ok, Err, Result

Chunk: TypeAlias = Metashape.Chunk
Document: TypeAlias = Metashape.Document


def create_document() -> Document:
    """Create a metashape document."""
    return Metashape.Document()


def load_document(path: Path) -> Result[Document, str]:
    """Loads the document from the given path."""
    if not path.exists():
        return Err(f"path does not exist: {path}")
    if not path.is_file():
        return Err(f"invalid document path: {path}")
    if not path.suffix in [".psz", ".psx"]:
        return Err(f"invalid document path: {path}")

    document = create_document()
    document.open(str(path))
    return Ok(document)


def save_document(document: Document, path: Path = None) -> Path:
    """Saves the document to the given path."""
    if not path:
        path = Path(document.path)
    return save_document_to_path(document, path)


def save_docoument_to_existing(document: Document) -> Path:
    """Saves the document to the existing path."""
    document.save()
    return Path(document.path)


def save_document_to_path(document: Document, path: Path) -> Path:
    """Saves the document to the given path."""
    assert path.suffix in [
        ".psz",
        ".psx",
    ], f"invalid path extension ('.psz' or '.psx'): {path}"
    document.save(str(path))
    return path


def create_chunk(document: Document, label: str = None) -> Chunk:
    """Creates a chunk for the given document."""
    chunk = document.addChunk()
    if label:
        chunk.label = label
    return chunk
