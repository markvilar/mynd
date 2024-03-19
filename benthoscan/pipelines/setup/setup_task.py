""" This module contains functionality for configuring a chunk with images,
references, reference accuracies, and camera calibrations. """

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, TypeAlias

from loguru import logger
from result import Ok, Err, Result

from benthoscan.containers import (
    FileRegistry,
    create_file_registry,
    DataTable,
    read_table,
)
from benthoscan.datatypes import CameraAssemblyFactory
from benthoscan.filesystem import find_files_with_extension
from benthoscan.project import Chunk

from .chunk_tasks import add_composed_images_to_chunk, add_camera_references


@dataclass
class ImageConfig:
    """Data class for image configuration."""

    directory: Path
    extensions: List[str]


@dataclass
class CameraConfig:
    """Data class for camera configuration."""

    name: str
    label_keys: List[str]


@dataclass
class ChunkConfig:
    """Data class for chunk configuration."""

    name: str
    images: ImageConfig
    camera: CameraConfig


def retrieve_image_files_from_registry(
    registry: FileRegistry,
    labels: Dict[int, str],
) -> Dict[int, Path]:
    """Retrieves images from a registry."""
    files: Dict[int, Path] = dict()
    for index, label in labels.items():
        if not label in registry:
            continue
        files[index] = registry[label]
    return files


def configure_chunk(
    chunk: Chunk,
    assembly_factory: CameraAssemblyFactory,
    config: ChunkConfig,
) -> None:
    """Configures a chunk with reference images."""
    
    # Find image files in directory
    image_files: List[Path] = find_files_with_extension(
        config.images.directory,
        config.images.extensions,
    )

    # Create file registry and add image files
    file_registry: FileRegistry = create_file_registry()
    file_registry.add_files(image_files)

    # Read references from file
    result: Result[DataTable, str] = read_table(config.reference_file)
    table = result.unwrap()

    # Get labels from camera config and references
    label_groups = dict()
    for key in config.camera.label_keys:
        label_groups[key] = table.get_field(key)

    # Retrieve image files from registry based on labels
    file_groups: Dict[str, Dict[int, Path]] = dict()
    for key in label_groups:
        file_groups[key] = retrieve_image_files_from_registry(
            file_registry,
            label_groups[key],
        )

    # Add image groups to chunk
    result: Result[int, str] = add_composed_images_to_chunk(
        chunk,
        file_collections=file_groups,
        group_order=config.camera.label_keys,
    )

    match result:
        case Ok(count):
            logger.info(f"Added image groups: {count}")
        case Err(message):
            logger.info(f"Failed to add grouped images: {message}")

    camera_references = create_camera_references_from_table(table, config.reference)

    # TODO: Add references
    result: Result[bool, str] = add_camera_references(chunk, camera_references)

    match result:
        case Ok(success):
            logger.info(f"Added reference: {success}")
        case Err(message):
            logger.info(f"Failed to add reference: {message}")

    # TODO: Configure camera calibration
