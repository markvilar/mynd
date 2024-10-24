"""Module for stereo helper functions."""

from collections.abc import Iterable
from typing import NamedTuple

import Metashape as ms

from mynd.camera import CameraID, CameraCalibration
from mynd.image import Image, ImageLoader
from mynd.io import read_image
from mynd.collections import GroupID, StereoCameraGroup
from mynd.utils.containers import Pair

from .camera_helpers import compute_camera_calibration


NativeSensorPair = Pair[ms.Sensor]
NativeCameraPair = Pair[ms.Camera]


class StereoFrames(NamedTuple):
    """Class representing a pair of stereo sensors and their corresponding camera pairs."""

    sensor_pair: NativeSensorPair
    camera_pairs: list[NativeCameraPair]


def get_stereo_group(chunk: ms.Chunk) -> list[StereoCameraGroup]:
    """Composes stereo collections for the sensors and cameras in the chunk.
    Stereo collections are based on master-slave pairs of sensor and their
    corresponding cameras."""

    sensor_pairs: set[NativeSensorPair] = _get_sensor_pairs(chunk)
    camera_pairs: set[NativeCameraPair] = _get_camera_pairs(chunk)

    stereo_frames: list[StereoFrames] = [
        _get_stereo_frames(sensor_pair, camera_pairs)
        for sensor_pair in sensor_pairs
    ]

    group_identifier: GroupID = GroupID(chunk.key, chunk.label)

    groups: list[StereoCameraGroup] = list()
    for frames in stereo_frames:

        calibrations: Pair[CameraCalibration] = Pair(
            first=compute_camera_calibration(frames.sensor_pair.first),
            second=compute_camera_calibration(frames.sensor_pair.second),
        )

        # Create pairs of camera identifiers
        camera_pairs: list[Pair[CameraID]] = generate_camera_pairs(
            frames.camera_pairs
        )

        # Create image loaders for all the cameras
        image_loaders: dict[CameraID, ImageLoader] = generate_image_loaders(
            frames.camera_pairs
        )

        group: StereoCameraGroup = StereoCameraGroup(
            group_identifier=group_identifier,
            calibrations=calibrations,
            camera_pairs=camera_pairs,
            image_loaders=image_loaders,
        )

        groups.append(group)

    return groups


def generate_camera_pairs(
    camera_pairs: list[NativeCameraPair],
) -> list[Pair[CameraID]]:
    """Creates a collection of camera pairs from stereo frames."""
    identifier_pairs: list[Pair[CameraID]] = [
        Pair(
            CameraID(cameras.first.key, cameras.first.label),
            CameraID(cameras.second.key, cameras.second.label),
        )
        for cameras in camera_pairs
    ]
    return identifier_pairs


def generate_image_loader(camera: ms.Camera) -> ImageLoader:
    """Generate an image loader from a Metashape camera."""

    def load_camera_image() -> Image:
        """Load an image from a Metashape camera."""
        return read_image(camera.photo.path).unwrap()

    return load_camera_image


def generate_image_loaders(
    camera_pairs: list[NativeCameraPair],
) -> dict[CameraID, ImageLoader]:
    """Generate image loaders for a collection of camera pairs."""

    image_loaders: dict[CameraID, ImageLoader] = dict()
    for cameras in camera_pairs:
        first_camera: CameraID = CameraID(
            cameras.first.key, cameras.first.label
        )
        second_camera: CameraID = CameraID(
            cameras.second.key, cameras.second.label
        )

        first_loader: ImageLoader = generate_image_loader(cameras.first)
        second_loader: ImageLoader = generate_image_loader(cameras.second)

        image_loaders[first_camera] = first_loader
        image_loaders[second_camera] = second_loader

    return image_loaders


def _get_stereo_frames(
    sensor_pair: NativeSensorPair,
    camera_pairs: Iterable[NativeCameraPair],
) -> StereoFrames:
    """Groups stereo cameras by matching the camera sensors with the sensor pair."""
    filtered_camera_pairs: list[NativeCameraPair] = [
        camera_pair
        for camera_pair in camera_pairs
        if camera_pair.first.sensor == sensor_pair.first
        and camera_pair.second.sensor == sensor_pair.second
    ]

    return StereoFrames(
        sensor_pair=sensor_pair, camera_pairs=filtered_camera_pairs
    )


def _get_sensor_pairs(chunk: ms.Chunk) -> set[NativeSensorPair]:
    """Gets master-slave pairs of sensors from a ms chunk."""
    stereo_sensors: set[NativeSensorPair] = set(
        [
            NativeSensorPair(sensor.master, sensor)
            for sensor in chunk.sensors
            if sensor.master != sensor
        ]
    )
    return stereo_sensors


def _get_camera_pairs(chunk: ms.Chunk) -> set[NativeCameraPair]:
    """Gets master-slave pairs of cameras from a ms chunk."""
    stereo_cameras: set[NativeCameraPair] = set(
        [
            NativeCameraPair(camera.master, camera)
            for camera in chunk.cameras
            if camera.master != camera
        ]
    )
    return stereo_cameras
