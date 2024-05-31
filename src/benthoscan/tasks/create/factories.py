"""Module for task specific project factories."""

from functools import partial
from typing import Callable

from result import Result

from benthoscan.project import (
    Chunk,
    Document,
    create_chunk,
    create_document,
    load_document,
)

from .config import ChunkConfig, DocumentConfig


DocumentResult = Result[Document, str]
DocumentFactory = Callable[[None], DocumentResult]


def create_document_factory(config: DocumentConfig) -> DocumentFactory:
    """Returns a document factory based on the given configuration."""
    if config.create_new:
        return partial(create_document)
    else:
        return partial(load_document, path=config.path)


ChunkFactory = Callable[[None], Chunk]


def create_chunk_factory(document: Document, config: ChunkConfig) -> Chunk:
    """Returns a chunk factory based on the given configuration."""
    return partial(create_chunk, document=document)
