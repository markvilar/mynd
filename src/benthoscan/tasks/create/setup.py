"""Module for setting up project data, i.e. chunks with image files, 
camera groups, and camera references."""

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from benthoscan.containers import DataTable, Registry, read_table
from benthoscan.filesystem import find_files_with_extension
from benthoscan.io import read_toml

from benthoscan.spatial import Vec3, SpatialReference, ReferenceSettings

from .config import ChunkConfig, ProjectConfig


@dataclass
class ChunkSetupData:
    """Class representing chunk setup data."""

    image_registry: Registry[str, Path]
    camera_registry: Registry[str, object]
    reference_registry: Registry[str, object]

    camera_settings: dict


@dataclass
class ProjectSetupData:
    """"""
    
    document_factory: object
    chunk_factory: object

    chunk_data: list[ChunkSetupData]


def prepare_chunk_data(config: ChunkConfig) -> ChunkSetupData:
    """Prepares a chunk for initialization by registering images, and
    loading cameras and references."""

    # Prepare camera data
    camera_table: DataTable = read_table(config.camera_file).unwrap()
    camera_settings: dict = read_toml(config.camera_settings).unwrap()

    logger.info(camera_settings["source"])
    logger.info(camera_settings["type"])

    image_registry: Registry[str, Path] = Registry[str, Path]()

    # Find files to populate the image registry
    image_files: list[Path] = find_files_with_extension(
        directory=config.image_directory,
        extensions=[".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    for file in image_files:
        image_registry.insert(file.name, file)

    input("press a key...")

    """
    logger.info(image_registry)
    logger.info(camera_table)
    logger.info(reference_table)
    logger.info(camera_settings)
    logger.info(reference_settings)
    """

    raise NotImplementedError("prepare_chunk is not implemented")


def prepare_project_data(config: ProjectConfig) -> ProjectSetupData:
    """Initializes a project by creating or loading a document,
    and populating it with chunks of data."""

    logger.info(config)
    input("Press a key...")

    # Use chunk factory to create a chunk
    chunk_setup_data: ChunkSetupData = prepare_chunk_data(chunk_config)

    result: Result[Path, str] = save_document(document, config.document.path)
    match result:
        case Ok(path):
            logger.info(f"saved document to {path}")
        case Err(message):
            logger.error("failed to save document")
            logger.error(message)
