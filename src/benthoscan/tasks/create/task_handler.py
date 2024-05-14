"""Module for management of the create task."""

from loguru import logger
from result import Result

from benthoscan.project import Chunk, Document, save_document
from benthoscan.runtime import Command

from .arguments import parse_arguments, create_config_from_arguments
from .data_handlers import prepare_chunk
from .config import ProjectConfig
from .factories import (
    ChunkFactory,
    DocumentFactory,
    create_chunk_factory,
    create_document_factory,
)


def initialize_project(config: ProjectConfig) -> None:
    """Initializes a project by creating or loading a document,
    and populating it with chunks of data."""

    # Use configuration to switch between different document factories
    document_factory: DocumentFactory = create_document_factory(config.document)

    # Use the factory to create a document
    result: Result[Document, str] = document_factory()
    if result.is_err():
        logger.error(result.err())
        return

    document: Document = result.ok()

    # Use each configuration to create and populate a chunk of data
    for chunk_config in config.chunks:

        # Create a factory depending on the chunk configuration
        chunk_factory: ChunkFactory = create_chunk_factory(document, chunk_config)

        # Use chunk factory to create a chunk
        chunk: Chunk = chunk_factory()

        prepare_chunk(chunk, chunk_config)


    result: Result[Path, str] = save_document(document, config.document.path)
    match result:
        case Ok(path):
            logger.info(f"saved document to {path}")
        case Err(message):
            logger.error("failed to save document")
            logger.error(message)


def handle_create_task(command: Command) -> None:
    """Handles a create task - processes arguments, creates configuration, and initializes project data."""

    result: Result[ProjectConfig, str] = create_config_from_arguments(command.arguments)

    if result.is_err():
        logger.error(result.err())
        return

    config: ProjectConfig = result.ok()

    # TODO: Validate config

    # Execute task
    initialize_project(config)
