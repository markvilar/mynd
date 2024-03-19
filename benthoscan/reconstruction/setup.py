""" This module contains functionality for configuring a chunk with images,
references, reference accuracies, and camera calibrations. """
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, TypeAlias

from loguru import logger
from result import Result

from benthoscan.filesystem import (
    FileRegistry, 
    create_file_registry,
    find_files_with_extension
)

from .chunk import Chunk, add_image_groups_to_chunk
from .reference import Reference, read_reference_from_file

@dataclass
class ImageConfig():
    """ Data class for image configuration. """
    directory: Path
    extensions: List[str]

@dataclass
class CameraConfig():
    """ Data class for camera configuration. """
    name: str
    label_keys: List[str]

@dataclass
class ReferenceConfig():
    """ Data class for reference configuration. """
    filepath: Path
    position_format: str
    position_fields: List[str]
    orientation_format: str
    orientation_fields: List[str]

@dataclass
class ChunkConfig():
    """ Data class for chunk configuration. """
    images: ImageConfig
    camera: CameraConfig
    reference: ReferenceConfig

def retrieve_image_files_from_registry(
    registry: FileRegistry,
    labels: Dict[int, str],
) -> Dict[int, Path]:
    """ Retrieves images from a registry. """
    files: Dict[int, Path] = dict()
    for index, label in labels.items():
        if not label in registry:
            continue
        files[index] = registry[label]
    return files

def configure_chunk(
    chunk: Chunk,
    config: ChunkConfig,
) -> None:
    """ Configures a chunk with reference images. """
    # Find image files in directory
    image_files: List[Path] = find_files_with_extension(
        config.images.directory,
        config.images.extensions,
    )
    
    # Create file registry and add image files
    file_registry: FileRegistry = create_file_registry()
    file_registry.add_files(image_files)

    # Read references from file
    result: Result[Reference, str] = read_reference_from_file(
        config.reference.filepath
    )
    references = result.unwrap()
    
    # Get labels from camera config and references
    label_groups = dict()
    for key in config.camera.label_keys:
        label_groups[key] = references.get_values(key)
   
    # Retrieve image files from registry based on labels
    file_groups = dict()
    for key in label_groups:
        file_groups[key] = retrieve_image_files_from_registry(
            file_registry,
            label_groups[key],
        )
    
    # TODO: Add image files to chunk
    # add_image_groups_to_chunk(chunk, image_groups, group_order)
