"""Module for functionality for setting up camera data for a project. 
The module handles setup of images, sensors, and spatial references."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import Metashape

from result import Ok, Err, Result

from ...cameras import Camera, MonocularCamera, StereoCamera
from ...containers import Registry
from ...spatial import SpatialReference
from ...utils.log import logger


ProgressCallback: TypeAlias = Callable[[float], None]


@dataclass
class ImageData:
    """Class representing image data."""

    filenames: list[str]
    filegroups: list[int]
    layout: object


def add_camera_images(
    chunk: Metashape.Chunk,
    cameras: list[Camera],
    image_registry: Registry[str, Path],
    progress_fun: ProgressCallback = lambda percent: None,
) -> Result[ImageData, str]:
    """Single dispatch function for adding camera images to a chunk."""

    match cameras[0]:
        case MonoCamera():
            return add_monocular_images(chunk, cameras, image_registry, progress_fun)
        case StereoCamera():
            return add_stereo_images(chunk, cameras, image_registry, progress_fun)
        case _:
            return Err(f"unsupported camera type: {type(cameras[0])}")


def add_monocular_images(chunk, cameras, image_registry, progress_fun) -> ImageData:
    """TODO"""

    raise NotImplementedError("add_monocular_images is not implemented")


def add_stereo_images(
    chunk: Metashape.Chunk,
    cameras: list[StereoCamera],
    image_registry: Registry[str, Path],
    progress_fun: ProgressCallback = lambda percent: None,
) -> ImageData:
    """Adds a collection of stereo image pairs to a chunk."""

    filenames: list[str] = list()
    filegroups: list[int] = list()
    for camera in cameras:
        if not camera.master in image_registry:
            logger.error(f"missing image: {camera.master}")
            continue
        if not camera.slave in image_registry:
            logger.error(f"missing image: {camera.slave}")
            continue

        master_image: Path = image_registry[camera.master]
        slave_image: Path = image_registry[camera.slave]

        if not master_image:
            logger.error(f"image does not exist: {master_image}")

        if not slave_image:
            logger.error(f"image does not exist: {slave_image}")

        filenames.extend([str(master_image), str(slave_image)])
        filegroups.append(2)

    data: ImageData = ImageData(filenames, filegroups, Metashape.MultiplaneLayout)

    try:
        chunk.addPhotos(
            filenames=data.filenames,
            filegroups=data.filegroups,
            layout=data.layout,
            progress=progress_fun,
        )
    except RuntimeError as error:
        return Err(f"failed to add stereo images: {error}")
    except BaseException as error:
        return Err(f"failed to add stereo images: {error}")

    return Ok(data)


def add_camera_group(
    chunk: Metashape.Chunk,
    cameras: list[Camera],
    image_registry: Registry[str, Path],
    progress_fun: ProgressCallback = lambda percent: None,
) -> Result[ImageData, str]:
    """Single dispatch function for adding a camera group to a chunk."""

    camera_types = [type(camera) for camera in cameras]

    match cameras[0]:
        case StereoCamera():
            return add_stereo_group(chunk, cameras, image_registry, progress_fun)
        case _:
            return Err(f"unsupported camera type: {type(cameras[0])}")


def add_stereo_group(
    chunk: Metashape.Chunk,
    cameras: list[StereoCamera],
    image_registry: Registry[str, Path],
    progress_fun: ProgressCallback = lambda percent: None,
) -> Result[None, str]:
    """Adds a stereo camera group to a chunk. The method adds stereo image pairs
    to the chunk, and configures the sensors for the stereo camera setup."""

    result: Result[ImageData, str] = add_stereo_images(chunk, cameras, image_registry)
    if result.is_err():
        return result

    # Get automatically created internal cameras
    internal_cameras: dict[str, Metashape.Camera] = {
        camera.label: camera for camera in chunk.cameras
    }

    # NOTE: Might changes this to be based on a major vote rather than the first camera
    # Metashape can create multiple sensors, so
    master_sensor: Metashape.Sensor = internal_cameras[cameras[0].master].sensor
    slave_sensor: Metashape.Sensor = internal_cameras[cameras[0].slave].sensor

    master_sensor.makeMaster()

    # TODO: Add sensor labels to camera group
    master_sensor.label: str = "stereo_master"
    slave_sensor.label: str = "stereo_slave"

    slave_sensor.reference.enabled = True
    slave_sensor.reference.location_enabled = True
    slave_sensor.reference.rotation_enabled = True

    # TODO: Move slave offset to config
    slave_sensor.reference.location = Metashape.Vector([0.07, 0.0, 0.0])
    slave_sensor.reference.rotation = Metashape.Vector([0.0, 0.0, 0.0])
    slave_sensor.reference.location_accuracy = Metashape.Vector([0.005, 0.005, 0.005])
    slave_sensor.reference.rotation_accuracy = Metashape.Vector([0.5, 0.5, 0.5])

    # NOTE: Might not be necessary
    slave_sensor.fixed_location = False
    slave_sensor.fixed_rotation = False

    # Reassign the sensors of the internal cameras to the extracted (and configured) sensors
    for camera in cameras:
        # Skip stereo pair if any of the two cameras are not found
        if not camera.master in internal_cameras:
            logger.error(f"missing camera: {camera.master}")
            continue
        if not camera.slave in internal_cameras:
            logger.error(f"missing camera: {camera.slave}")
            continue

        master_camera: Metashape.Camera = internal_cameras[camera.master]
        slave_camera: Metashape.Camera = internal_cameras[camera.slave]

        master_camera.master: Metashape.Camera = master_camera
        slave_camera.master: Metashape.Camera = master_camera

        master_camera.sensor = master_sensor
        slave_camera.sensor = slave_sensor

    return Ok(None)


def add_camera_references(
    chunk: Metashape.Chunk,
    cameras: list[Camera],
    references: Registry[str, SpatialReference],
) -> Result[None, str]:
    """TODO"""

    for camera in chunk.cameras:
        if not camera.label in references:
            continue

        reference: SpatialReference = references[camera.label]
        reference_result: Result[None, str] = add_camera_reference(camera, reference)

        if reference_result.is_err():
            logger.error(f"failed to add reference to camera: {camera.label}")

    return Ok(None)


def add_camera_reference(
    camera: Metashape.Camera,
    reference: SpatialReference,
) -> Result[None, str]:
    """Updates the reference of a Metashape camera with the values from a camera
    reference."""

    # TODO: Consider making reference position and orientation optional

    camera.reference.enabled = True
    camera.reference.location_enabled = True
    camera.reference.rotation_enabled = True

    camera.reference.location = Metashape.Vector(
        (
            reference.geolocation.longitude,
            reference.geolocation.latitude,
            reference.geolocation.height,
        )
    )

    camera.reference.rotation = Metashape.Vector(
        (
            reference.orientation.heading,
            reference.orientation.pitch,
            reference.orientation.roll,
        )
    )

    if reference.has_geolocation_accuracy:
        camera.reference.location_accuracy = Metashape.Vector(
            (
                reference.geolocation_accuracy.x,
                reference.geolocation_accuracy.y,
                reference.geolocation_accuracy.z,
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

    return Ok(None)
