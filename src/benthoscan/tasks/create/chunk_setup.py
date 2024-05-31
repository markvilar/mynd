"""Module for functionality to configuring a chunk with images, references, 
and camera calibrations."""

from pathlib import Path
from typing import Dict, List, TypeAlias

import Metashape

from loguru import logger
from result import Ok, Err, Result

from benthoscan.containers import Registry
from benthoscan.datatypes import CameraAssembly, CameraAssemblyFactory
from benthoscan.project import Chunk

from .camera_setup import add_assembly_images, add_assembly_references


FileRegistry: TypeAlias = Registry[str, Path]


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
        found_all_images = all(found.values())

        if not found_all_images:
            logger.warning("missing image file in assembly: {assembly}")
            stats["missing"].append(assembly)
        else:
            stats["found"].append(assembly)

    return Ok(stats)


def configure_chunk(
    chunk: Chunk,
    assembly_factory: CameraAssemblyFactory,
    registry: FileRegistry,
) -> Result[Dict, str]:
    """Configures a chunk with cameras (image files and spatial references)."""

    # Coordinate system used for reference data
    chunk.crs = Metashape.CoordinateSystem("EPSG::4326")

    # Coordinate system used for camera reference data
    chunk.camera_crs = Metashape.CoordinateSystem("EPSG::4326")

    # TODO: Move default values to config file
    chunk.camera_location_accuracy = Metashape.Vector((2.0, 2.0, 0.1))
    chunk.camera_rotation_accuracy = Metashape.Vector((180.0, 5.0, 5.0))

    assemblies: List[CameraAssembly] = assembly_factory()

    stats = dict()

    stats["validation"]: Dict[str, List] = check_assembly_images_in_registry(
        registry, assemblies
    ).unwrap()

    stats["images"]: Dict[str, List] = add_assembly_images(
        chunk, assemblies, registry
    ).unwrap()

    stats["reference"]: Dict[str, List] = add_assembly_references(
        chunk, assemblies
    ).unwrap()

    # TODO: Add camera calibration?
    # TODO: Configure sensors

    return Ok(stats)
