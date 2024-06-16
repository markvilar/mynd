""" Metashape document functions. """

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias, Callable

import Metashape

from result import Ok, Err, Result


Chunk: TypeAlias = Metashape.Chunk
Document: TypeAlias = Metashape.Document


DOCUMENT_EXTENSIONS = [".psz", ".psx"]


@dataclass
class ProjectData:
    """Class representing project data."""

    document: Document
    chunks: list[Chunk]
    document_path: Path


def load_project(document_path: Path) -> Result[ProjectData, str]:
    """TODO"""
    result: Result[Document, str] = load_document(document_path)

    match result:
        case Ok(document):
            chunks: list[Chunk] = document.chunks
            project: ProjectData = ProjectData(
                document=document, chunks=chunks, document_path=document_path
            )
            return Ok(project)
        case Err(error):
            return Err(error)
        case _:
            return Err("unknown error during project loading")


def save_project(project: ProjectData, document_path: Path = None) -> Result[None, str]:
    """TODO"""
    if not document_path:
        document_path: Path = project.document_path

    if not document_path.exists():
        return Err(f"document path does not exist: {document_path}")

    if not document_path.suffix in DOCUMENT_EXTENSIONS:
        return Err(f"invalid document extension: {document_path.suffix}")

    result: Result[Path, str] = save_document(project.document, document_path)

    match result:
        case Ok(path):
            return Ok(None)
        case Err(error):
            return Err(error)


def create_document() -> Document:
    """Create a metashape document."""
    return Document()


def load_document(path: Path) -> Result[Document, str]:
    """Loads the document from the given path."""
    if not path.exists():
        return Err(f"path does not exist: {path}")
    if not path.is_file():
        return Err(f"document path is not a file: {path}")
    if not path.suffix in DOCUMENT_EXTENSIONS:
        return Err(f"invalid document extension: {path}")

    document: Document = create_document()
    try:
        document.open(str(path))
    except IOError as error:
        return Err(error)
    return Ok(document)


def save_document(document: Document, path: Path = None) -> Result[Path, str]:
    """Saves the document to the given path."""
    if not path:
        return save_document_to_path(document, Path(document.path))
    else:
        return save_document_to_path(document, path)


def save_document_to_path(document: Document, path: Path) -> Result[Path, str]:
    """Saves the document to the given path."""
    if not path.suffix in DOCUMENT_EXTENSIONS:
        return Err(f"invalid document extension: {path}")

    try:
        document.save(str(path))
    except OSError as error:
        return Err(str(error))
    return Ok(path)


def create_chunk(document: Document, label: str = None) -> Chunk:
    """Creates a chunk for the given document."""
    chunk = document.addChunk()
    if label:
        chunk.label = label
    return chunk
