"""Functions for chunk configuration - adding images, cameras, and reference to chunks."""

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, TypeAlias

import Metashape

from loguru import logger
from result import Ok, Err, Result

from benthoscan.containers import Registry
from benthoscan.datatypes import Camera, CameraAssembly
from benthoscan.project import Chunk

ProgressCallback: TypeAlias = Callable[[float], None]
FileRegistry: TypeAlias = Registry[str, Path]


def add_assembly_images(
    chunk: Chunk,
    assemblies: List[CameraAssembly],
    registry: FileRegistry,
    progress_fun: ProgressCallback = lambda percent: None,
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

    filenames = [str(filename) for filename in filenames]

    logger.info(f"Filenames:  {len(filenames)}")
    logger.info(f"Filegroups: {len(filegroups)}")

    try:
        chunk.addPhotos(
            filenames=filenames,
            filegroups=filegroups,
            layout=Metashape.MultiplaneLayout,
            progress=progress_fun,
        )
    except RuntimeError as error:
        return Err(str(error))

    success_count, input_count = len(chunk.cameras), len(filenames)
    if input_count != success_count:
        # TODO: Retrieve the camera labels for the files that have not been added
        return Err(
            f"failed to add all cameras to chunk: {input_count} input, {success_count} added"
        )

    stats = {
        "filename_count": len(filenames),
        "filegroup_count": len(filegroups),
        "added_cameras": len(chunk.cameras),
        "given_cameras": len(filenames),
    }

    return Ok(stats)


def add_camera_reference(
    camera: Metashape.Camera,
    reference: Camera.Reference,
) -> bool:
    """Updates the reference of a Metashape camera with the values from a camera
    reference."""
    # Update state to make a potentially old reference invalid
    camera.reference.enabled = False
    camera.reference.location_enabled = False
    camera.reference.rotation_enabled = False

    if reference.has_position:
        camera.reference.enabled = True
        camera.reference.location_enabled = True
        camera.reference.location = Metashape.Vector(
            (
                reference.position.x,
                reference.position.y,
                reference.position.z,
            )
        )

    if reference.has_position_accuracy:
        camera.reference.location_accuracy = Metashape.Vector(
            (
                reference.position_accuracy.x,
                reference.position_accuracy.y,
                reference.position_accuracy.z,
            )
        )

    if reference.has_orientation:
        camera.reference.rotation_enabled = True
        camera.reference.rotation = Metashape.Vector(
            (
                reference.orientation.x,
                reference.orientation.y,
                reference.orientation.z,
            )
        )

    if reference.has_orientation_accuracy:
        camera.reference.rotation_accuracy = Metashape.Vector(
            (
                reference.orientation_accuracy.x,
                reference.orientation_accuracy.y,
                reference.orientation_accuracy.z,
            )
        )

    return True


def add_assembly_references(
    chunk: Chunk,
    assemblies: List[CameraAssembly],
    progress_fun: ProgressCallback = lambda percent: None,
) -> Result[Dict, str]:
    """Adds references to the cameras in a collection of camera assemblies."""

    stats = {
        "successes": list(),
        "failures": list(),
    }

    # Set up a lookup table for the chunk cameras
    chunk_cameras = {camera.label: camera for camera in chunk.cameras}

    for assembly in assemblies:
        for camera in assembly.cameras:
            key = camera.labels.camera

            if not camera.has_reference:
                continue

            if not key in chunk_cameras:
                logger.error(f"unable to find camera in chunk: {key}")
                continue

            chunk_camera = chunk_cameras[key]

            # Add reference to chunk camera
            success = add_camera_reference(chunk_camera, camera.reference)

            if not success:
                logger.warning(f"failed to add reference to camera: {key}")
                stats["failures"].append(key)
            else:
                stats["successes"].append(key)

    return Ok(stats)
