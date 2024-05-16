"""Module for handling chunk data, i.e. image files, camera groups, and camera references."""

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from benthoscan.containers import DataTable, Registry, read_table
from benthoscan.filesystem import find_files_with_extension
from benthoscan.io import read_toml
from benthoscan.project import Chunk


from benthoscan.spatial import Vec3, SpatialReference, ReferenceSettings

from .config import ChunkConfig, ProjectConfig
from .factories import create_chunk_factory, create_document_factory

@dataclass
class ChunkSettings:
    """Class representing chunk settings."""

    camera: object
    reference: object


@dataclass
class ChunkData:
    """Class representing chunk data."""

    image_registry: Registry[str, Path]
    camera_registry: Registry[str, object]
    reference_loader: object


def prepare_chunk_data(chunk: Chunk, config: ChunkConfig) -> Chunk:
    """Prepares a chunk for initialization by registering images, and
    loading cameras and references."""

    image_registry: Registry[str, Path] = Registry[str, Path]()

    # Find files to populate the image registry
    image_files: list[Path] = find_files_with_extension(
        directory=config.directories.images,
        extensions=[".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    for file in image_files:
        image_registry.insert(file.name, file)

    # Prepare camera data
    camera_table: DataTable = read_table(config.directories.cameras / config.files.cameras).unwrap()
    camera_settings: dict = read_toml(config.settings.cameras).unwrap()

    # TODO: Use settings to create camera reader

    logger.info(camera_settings["source"])
    logger.info(camera_settings["type"])


    reference_table: DataTable = read_table(config.directories.cameras / config.files.references).unwrap()

    # TODO: Create reference groups from table

    

    reference_settings: dict = read_toml(config.settings.references).unwrap()

    input("press a key...")

    """
    logger.info(image_registry)
    logger.info(camera_table)
    logger.info(reference_table)
    logger.info(camera_settings)
    logger.info(reference_settings)
    """

    raise NotImplementedError("prepare_chunk is not implemented")


def prepare_project_data(config: ProjectConfig) -> None:
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

        prepare_chunk_data(chunk, chunk_config)

    result: Result[Path, str] = save_document(document, config.document.path)
    match result:
        case Ok(path):
            logger.info(f"saved document to {path}")
        case Err(message):
            logger.error("failed to save document")
            logger.error(message)

