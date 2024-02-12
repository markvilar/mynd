""" Metashape document functions. """
from pathlib import Path

import Metashape

Chunk = Metashape.Chunk
Document = Metashape.Document

def create_document(path: Path) -> Document:
    """ Create a metashape document. """
    assert path.suffix == ".psz", f"file path extension is not '.psz' {path}"
    document = Metashape.Document()
    document.save(str(path))
    return document

def load_document(path: Path) -> Document:
    """ Loads the document from the given path. """
    return document.load(str(path))

def save_document(document: Document, path: Path) -> Path:
    """ Saves the document to the given path. """
    document.save(str(path))
    return path

def create_chunk(document: Document) -> Chunk:
    """ Creates a chunk for the given document"""
    return document.addChunk()
