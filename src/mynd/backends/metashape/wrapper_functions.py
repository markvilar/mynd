"""Module for functionality for setting up camera data for a project.
The module handles setup of images, sensors, and spatial references."""

from collections.abc import Callable
from typing import NamedTuple, TypeAlias

import Metashape

from ...camera import Sensor
from ...spatial import SpatialReference
from ...utils.log import logger
from ...utils.result import Ok, Err, Result


ProgressCallback: TypeAlias = Callable[[float], None]


class ImageIngestResult(NamedTuple):
    """Class representing an image ingestion result."""

    added_sensors: set[Metashape.Sensor]
    added_cameras: set[Metashape.Camera]
    sensor_map: dict[Metashape.Sensor, Metashape.Camera]


def add_images_to_chunk(
    chunk: Metashape.Chunk,
    filenames: list[str],
    filegroups: list[int],
    progress_fun: ProgressCallback = lambda percent: None,
) -> Result[ImageIngestResult, str]:
    """Adds image files to a Metashape chunk."""

    before_sensors: list[Metashape.Sensor] = chunk.sensors
    before_cameras: list[Metashape.Camera] = chunk.cameras

    try:
        chunk.addPhotos(
            filenames=filenames,
            filegroups=filegroups,
            layout=Metashape.MultiplaneLayout,
            load_reference=False,
            load_xmp_calibration=False,
            load_xmp_orientation=False,
            load_xmp_accuracy=False,
            load_xmp_antenna=False,
            load_rpc_txt=False,
            progress=progress_fun,
        )
    except RuntimeError as error:
        return Err(f"failed to image files: {error}")
    except BaseException as error:
        return Err(f"failed to image files: {error}")

    after_sensors: list[Metashape.Sensor] = chunk.sensors
    after_cameras: list[Metashape.Camera] = chunk.cameras

    added_sensors: set[Metashape.Sensor] = set(after_sensors) - set(before_sensors)
    added_cameras: set[Metashape.Camera] = set(after_cameras) - set(before_cameras)

    sensor_map: dict[Metashape.Sensor, list[Metashape.Camera]] = dict()
    for camera in added_cameras:
        if camera.sensor not in added_sensors:
            logger.warning(
                f"sensor for added camera does not match added sensors: {camera.key}"
            )
            continue
        elif camera.sensor not in sensor_map:
            sensor_map[camera.sensor] = list()

        sensor_map[camera.sensor].append(camera)

    return Ok(
        ImageIngestResult(
            added_sensors=added_sensors,
            added_cameras=added_cameras,
            sensor_map=sensor_map,
        )
    )


def reconfigure_camera_reference(
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


def reconfigure_sensor_attributes(configured: Sensor, native: Metashape.Sensor) -> None:
    """Reconfigures the attributes of a Metashape sensor based on the given configuration."""

    # TODO: Add support for other sensor types
    native.type: Metashape.Sensor.Type = Metashape.Sensor.Type.Frame
    native.label: str = configured.label

    native.width: int = configured.width
    native.height: int = configured.height

    native.fixed_location: bool = configured.fixed_location
    native.fixed_rotation: bool = configured.fixed_rotation

    if configured.has_bands:
        native.bands: list[str] = [
            band.get("name", "unknown") for band in configured.bands
        ]
        native.black_level: list[float] = [
            band.get("black_level", 0.0) for band in configured.bands
        ]
        native.sensitivity: list[float] = [
            band.get("sensitivity", 0.0) for band in configured.bands
        ]

    # Assign reference
    if configured.has_location:
        native.reference.location = Metashape.Vector(configured.location)
    if configured.has_rotation:
        native.reference.rotation = Metashape.Vector(configured.rotation)
    if configured.has_location_accuracy:
        native.reference.location_accuracy = Metashape.Vector(
            configured.location_accuracy
        )
    if configured.has_rotation_accuracy:
        native.reference.rotation_accuracy = Metashape.Vector(
            configured.rotation_accuracy
        )
