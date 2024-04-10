"""This module contains functionality for configuring a chunk with images,
references, and camera calibrations."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, TypeAlias

from loguru import logger
from result import Ok, Err, Result

from benthoscan.containers import FileRegistry
from benthoscan.datatypes import CameraAssembly, CameraAssemblyFactory
from benthoscan.project import Chunk

from .chunk_tasks import add_assembly_images, add_assembly_references


def check_assembly_images_in_registry(
    registry: FileRegistry, assemblies: List[CameraAssembly]
) -> None:
    """Checks if the images of the camera assemblies are in the file
    registry."""
    stats = {
        "found": list(),
        "missing": list(),
    }

    for assembly in assemblies:

        found_cameras = list()
        missing_cameras = list()

        found = {camera: camera.labels.image in registry for camera in assembly.cameras}
        found_all = all(found.values())

        if not found_all:
            logger.error("missing image file in assembly: {assembly}")

    return Ok(stats)


def configure_chunk(
    chunk: Chunk,
    assembly_factory: CameraAssemblyFactory,
    registry: FileRegistry,
) -> None:
    """Configures a chunk with reference images."""

    assemblies: List[CameraAssembly] = assembly_factory()

    # TODO: Check that image files are in registry
    stats: Dict[str, List] = check_assembly_images_in_registry(
        registry, assemblies
    ).unwrap()

    # TODO: Add camera assemblies to chunk
    result: int = add_assembly_images(chunk, assemblies, registry).unwrap()

    # TODO: Add references
    result = add_assembly_references(chunk, assemblies).unwrap()
    
    # TODO: Configure camera calibration
