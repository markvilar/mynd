"""Module for stereo helper functions."""

from collections.abc import Iterable
from typing import NamedTuple

import Metashape as ms

from mynd.camera import CameraCalibration
from mynd.image import Image, ImageLoader
from mynd.collections import StereoCameraGroup
from mynd.utils.containers import Pair

from .camera_helpers import compute_camera_calibration
from .image_helpers import convert_image


SensorPair = Pair[ms.Sensor]
CameraPair = Pair[ms.Camera]


class StereoFrames(NamedTuple):
    """Class representing a pair of stereo sensors and their corresponding camera pairs."""

    sensor_pair: SensorPair
    camera_pairs: list[CameraPair]


def get_stereo_group(chunk: ms.Chunk) -> list[StereoCameraGroup]:
    """Composes stereo collections for the sensors and cameras in the chunk.
    Stereo collections are based on master-slave pairs of sensor and their
    corresponding cameras."""

    sensor_pairs: set[SensorPair] = _get_sensor_pairs(chunk)
    camera_pairs: set[CameraPair] = _get_camera_pairs(chunk)

    stereo_frames: list[StereoFrames] = [
        _get_stereo_frames(sensor_pair, camera_pairs)
        for sensor_pair in sensor_pairs
    ]

    groups: list[StereoCameraGroup] = list()
    for frames in stereo_frames:

        calibrations: Pair[CameraCalibration] = Pair(
            first=compute_camera_calibration(frames.sensor_pair.first),
            second=compute_camera_calibration(frames.sensor_pair.second),
        )

        image_loaders: list[Pair[ImageLoader]] = generate_image_loader_pairs(
            frames.camera_pairs
        )

        group: StereoCameraGroup = StereoCameraGroup(
            calibrations=calibrations,
            image_loaders=image_loaders,
        )

        groups.append(group)

    return groups


ImagePair = Pair[Image]
CameraPair = Pair[ms.Camera]


def generate_image_loader(camera: ms.Camera) -> ImageLoader:
    """Generate an image loader from a Metashape camera."""

    def load_camera_image() -> Image:
        """Load an image from a Metashape camera."""
        return convert_image(camera.image())

    return load_camera_image


def generate_image_loader_pairs(
    camera_pairs: Iterable[CameraPair],
) -> list[Pair[ImageLoader]]:
    """Generate image loaders for a collection of camera pairs."""

    loaders: list[Pair[ImageLoader]] = [
        Pair(
            generate_image_loader(pair.first),
            generate_image_loader(pair.second),
        )
        for pair in camera_pairs
    ]

    return loaders


def _get_stereo_frames(
    sensor_pair: SensorPair,
    camera_pairs: Iterable[CameraPair],
) -> StereoFrames:
    """Groups stereo cameras by matching the camera sensors with the sensor pair."""
    filtered_camera_pairs: list[CameraPair] = [
        camera_pair
        for camera_pair in camera_pairs
        if camera_pair.first.sensor == sensor_pair.first
        and camera_pair.second.sensor == sensor_pair.second
    ]

    return StereoFrames(
        sensor_pair=sensor_pair, camera_pairs=filtered_camera_pairs
    )


def _get_sensor_pairs(chunk: ms.Chunk) -> set[SensorPair]:
    """Gets master-slave pairs of sensors from a ms chunk."""
    stereo_sensors: set[SensorPair] = set(
        [
            SensorPair(sensor.master, sensor)
            for sensor in chunk.sensors
            if sensor.master != sensor
        ]
    )
    return stereo_sensors


def _get_camera_pairs(chunk: ms.Chunk) -> set[CameraPair]:
    """Gets master-slave pairs of cameras from a ms chunk."""
    stereo_cameras: set[CameraPair] = set(
        [
            CameraPair(camera.master, camera)
            for camera in chunk.cameras
            if camera.master != camera
        ]
    )
    return stereo_cameras
