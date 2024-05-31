""" Metashape document functions. """

from pathlib import Path
from typing import TypeAlias, Callable

import Metashape

from result import Ok, Err, Result

Chunk: TypeAlias = Metashape.Chunk
Document: TypeAlias = Metashape.Document

ChunkFactory = Callable[[str], Chunk]
DocumentFactory = Callable[[None], Document]


DOCUMENT_EXTENSIONS = [".psz", ".psx"]


CreateResult = Result[Document, str]


def create_document(path: Path = None) -> CreateResult:
    """Create a metashape document."""
    if not path:
        return Ok(Document())

    document: Document = Document()
    result: SaveResult = save_document(document, path)

    match result:
        case Ok(save_path):
            return Ok(document)
        case Err(message):
            return Err(message)


def load_document(path: Path) -> CreateResult:
    """Loads the document from the given path."""
    if not path.exists():
        return Err(f"path does not exist: {path}")
    if not path.is_file():
        return Err(f"document path is not a file: {path}")
    if not path.suffix in DOCUMENT_EXTENSIONS:
        return Err(f"invalid document extension: {path}")

    document = create_document()
    document.open(str(path))
    return Ok(document)


SaveResult = Result[Path, str]


def save_document(document: Document, path: Path = None) -> SaveResult:
    """Saves the document to the given path."""
    if not path:
        return save_document_to_path(document, Path(document.path))
    else:
        return save_document_to_path(document, path)


def save_document_to_path(document: Document, path: Path) -> SaveResult:
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
