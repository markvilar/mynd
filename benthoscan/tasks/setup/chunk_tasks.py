""" Functions for """

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple, TypeAlias

import Metashape

from loguru import logger
from result import Ok, Err, Result

from benthoscan.containers import FileRegistry
from benthoscan.datatypes import CameraAssembly
from benthoscan.project import Chunk

GroupKey: TypeAlias = str
Index: TypeAlias = int


def add_assembly_images(
    chunk: Chunk,
    assemblies: List[CameraAssembly],
    registry: FileRegistry,
    progress_fun: Callable[[float], None] = lambda percent: None,
) -> Result[int, str]:
    """Adds multiplane images from camera assemblies to the chunk. The image
    paths are retrieved from the file registry before being add into Metashape."""

    counts = [assembly.count for assembly in assemblies]

    def all_identical(list):
        """Internal function that checks if all list elements are equal."""
        return len(set(list)) == 1

    # Check that all assemblies have the same number of camera counts
    if not all_identical(counts):
        return Err("the number of cameras in all assemblies are not equal")

    # For each assembly - get image paths and count
    filenames, filegroups = list(), list()
    for assembly in assemblies:
        filenames.extend([registry[camera.labels.image] for camera in assembly.cameras])
        filegroups.append(assembly.count)

    try:
        chunk.addPhotos(
            filenames=filenames,
            filegroups=filegroups,
            layout=Metashape.MultiplaneLayout,
            progress=progress_fun,
        )
    except RuntimeError as error:
        return Err(str(error))

    return Ok(len(filegroups))


def add_assembly_references(
    chunk: Chunk,
    assemblies: List[CameraAssembly],
    progress_fun: Callable[[float], None] = lambda percent: None,
) -> Result[int, str]:
    """TODO"""

    for camera in chunk.cameras:
        logger.info(camera)

    raise NotImplementedError


def add_camera_references(
    chunk: Chunk,
    camera_references,
) -> Result[bool, str]:
    """Add reference from memory."""

    logger.info(f"Reference: {reference.fields}")
    logger.info(f"Config:    {config}")

    input("Press a key...")

    # TODO: Get reference keys
    labels = list(reference.get_field(config.label_field).values())
    labels = list(reference.get_field(config.label_field).values())

    # labels = list(reference.get_field("stereo_left_label").values())

    reference_data = reference.items()

    for item in reference_data:
        logger.info(f"Index: {item}")

    input("Press a key...")

    # Camera lookup
    camera_lookup = dict([(camera.label, camera) for camera in chunk.cameras])

    for label in labels:
        logger.info(f"Label:  {label}")

    for camera in chunk.cameras:
        logger.info(f"Camera: {camera.label}")
        if camera.label in labels:
            logger.info("Left")
        else:
            logger.info("Unknown")

    return Ok(True)
