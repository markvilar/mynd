"""Test functionality for add a camera group to Metashape."""

from pathlib import Path
from typing import NamedTuple

import Metashape


from ...cameras import Sensor, Frame
from ...containers import Registry
from ...project import CameraGroupData
from ...spatial import SpatialReference
from ...utils.log import logger
from ...utils.result import Ok, Err, Result

from .wrapper_functions import (
    ImageIngestResult,
    reconfigure_sensor_attributes,
    reconfigure_camera_reference,
    add_images_to_chunk,
)


def add_camera_group(
    chunk: Metashape.Chunk, camera_group: CameraGroupData
) -> Result[None, str]:
    """Adds a camera group to a Metashape chunk."""

    # TODO: Move chunk and camera CRS to config
    chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
    chunk.camera_crs = Metashape.CoordinateSystem("EPSG::4326")

    # Add cameras and sensors from the group frames and images
    add_frames_to_chunk(chunk, camera_group.frames, camera_group.images)

    # Add camera references from the group reference registry
    add_camera_references_to_chunk(chunk, camera_group.references)

    # TODO: Return statistics from the ingested data
    return Ok(None)


class FileGroup(NamedTuple):
    """Class representing a file group."""

    names: list[str]
    counts: list[int]


def convert_frames_to_filegroups(
    frames: list[Frame],
    images: Registry[str, Path],
) -> Result[FileGroup, str]:
    """Converts a collection of frames to a file group. Validates that all frames
    have the same sensors, and that all the frame images are registered."""

    # Validate that all frames have the same sensors
    sensor_sets: list[set[Sensor]] = [set(frame.sensors) for frame in frames]
    is_all_equal: bool = check_all_equal(sensor_sets)

    if not is_all_equal:
        return Err("not all frames have the same set of sensors")

    filenames: list[str] = list()
    filecounts: list[int] = list()

    for frame in frames:
        missing_images: list[str] = [
            key for key in frame.image_keys if key not in images
        ]

        if missing_images:
            logger.warning(f"frame {frame.key} missing images: {missing_images}")
            continue

        image_paths: list[Path] = [images.get(key) for key in frame.image_keys]

        filenames.extend([str(path) for path in image_paths])
        filecounts.extend([len(image_paths)])

    return Ok(FileGroup(names=filenames, counts=filecounts))


def map_frame_sensors_to_keys(frames: list[Frame]) -> dict[Sensor, list[str]]:
    """Map the sensors to the image keys for every frame in a collection of frames."""
    sensor_images: dict[Sensor, list[str]] = dict()

    for frame in frames:
        for sensor, image_key in frame.components.items():
            if sensor not in sensor_images:
                sensor_images[sensor] = list()
            sensor_images[sensor].append(image_key)

    return sensor_images


def filter_cameras_based_on_label(
    labels: list[str],
    cameras: list[Metashape.Camera],
) -> list[Metashape.Camera]:
    """Filters cameras based on their label."""
    return [camera for camera in cameras if camera.label in labels]


class SensorMapping(NamedTuple):
    """Class representing a map from external to internal sensor."""

    external_sensor: Sensor
    native_sensor: Metashape.Sensor


def map_sensor_based_on_majority(
    sensor: Sensor,
    cameras: list[Metashape.Camera],
) -> Result[SensorMapping, str]:
    """Creates a mapping from an external sensor to Metashape"""

    candidate_sensors: list[Metashape.Sensor] = [camera.sensor for camera in cameras]

    if len(candidate_sensors) == 0:
        return Err(f"found no mapping from sensor: {sensor.key}")

    # Since cameras might have different sensors assigned to them, we reassign based
    # on a majority vote
    selected_sensor: Metashape.Sensor = max(
        set(candidate_sensors), key=candidate_sensors.count
    )

    return Ok(SensorMapping(external_sensor=sensor, native_sensor=selected_sensor))


def reconfigure_generated_sensors(
    frames: list[Frame],
    cameras: list[Metashape.Camera],
) -> None:
    """Reconfigures camera sensors generated by Metashape by reassigning the sensor
    for every camera captured by the same sensor."""

    # Create map from sensor to image keys
    sensor_to_images: dict[Sensor, list[str]] = map_frame_sensors_to_keys(frames)

    master_sensor: Metashape.Sensor = None
    mappings: list[SensorMapping] = list()
    for sensor, image_keys in sensor_to_images.items():

        filtered_cameras: list[Metashape.Camera] = filter_cameras_based_on_label(
            labels=image_keys,
            cameras=cameras,
        )

        mapping: SensorMapping = map_sensor_based_on_majority(
            sensor=sensor,
            cameras=filtered_cameras,
        ).unwrap()

        for camera in filtered_cameras:
            camera.sensor = mapping.native_sensor

        if mapping.external_sensor.master:
            master_sensor = mapping.native_sensor

        mappings.append(mapping)

    if not master_sensor:
        return Err("found no master sensor in frame")

    # Make internal master sensor master and reassign master sensor attribute
    for mapping in mappings:
        if mapping.native_sensor == master_sensor:
            mapping.native_sensor.makeMaster()

        mapping.native_sensor.master = master_sensor
        reconfigure_sensor_attributes(mapping.external_sensor, mapping.native_sensor)


def reconfigure_generated_cameras(
    frames: list[Frame],
    cameras: list[Metashape.Camera],
) -> None:
    """Reconfigures cameras generated by Metashape by properly assigning the master camera
    for the cameras in every frame."""

    camera_map: dict[str, Metashape.Camera] = {
        camera.label: camera for camera in cameras
    }

    for frame in frames:
        master = frame.master_sensor
        master_key: str = frame.get(master)

        master_camera: Metashape.Camera = camera_map.get(master_key)

        if not master_camera:
            continue

        for key in frame.image_keys:
            camera = camera_map.get(key)

            if camera:
                camera.master = master_camera


def add_frames_to_chunk(
    chunk: Metashape.Chunk, frames: list[Frame], images: Registry[str, Path]
) -> Result[None, str]:
    """Adds frames, i.e. sensors and images, to a Metashape chunk."""

    # Convert the frames into filegroups that can be added to Metashape
    filegroup: FileGroup = convert_frames_to_filegroups(frames, images).unwrap()

    # Add the image files to Metashape to automatically generate cameras and sensors
    ingestion: ImageIngestResult = add_images_to_chunk(
        chunk, filegroup.names, filegroup.counts
    ).unwrap()

    # Validate the generated sensors by reassigning the master and camera sensors
    reconfigure_generated_sensors(frames, ingestion.added_cameras)

    # Validate the generated cameras by reassigning the master cameras
    reconfigure_generated_cameras(frames, ingestion.added_cameras)


def add_camera_references_to_chunk(
    chunk: Metashape.Chunk,
    references: Registry[str, SpatialReference],
) -> Result[None, str]:
    """Adds reference to the cameras in a Metashape chunk. Cameras are
    selected if their label matches the reference key."""

    for camera in chunk.cameras:
        if camera.label not in references:
            continue

        reference: SpatialReference = references[camera.label]
        reference_result: Result[None, str] = reconfigure_camera_reference(
            camera, reference
        )

        if reference_result.is_err():
            logger.error(f"failed to add reference to camera: {camera.label}")

    return Ok(None)


def check_uniform_type(items: list[object]) -> Result[type, str]:
    """Checks whether a collection of items are of the same type."""

    item_types: set[type] = set([type(item) for item in items])
    is_uniform: bool = len(item_types) == 1

    if not is_uniform:
        return Err(f"types are not uniform: {items}")

    uniform_type: type = next(iter(item_types))
    return Ok(uniform_type)


def check_all_equal(items: list[object]) -> bool:
    """Checks whether all items in a collection is equal."""
    template = items[0]
    is_equal: list[bool] = [item == template for item in items]
    return all(is_equal)
