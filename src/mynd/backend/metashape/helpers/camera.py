"""Module for camera helper functions."""

from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

import Metashape as ms
import numpy as np

from mynd.camera import CameraID, CameraCalibration, SensorID
from mynd.collections import CameraGroup, StereoCameraGroup
from mynd.image import ImageLoader
from mynd.utils.containers import Pair

from .image import generate_image_loader_pairs

from ..common.math import matrix_to_array, vector_to_array


def get_camera_attribute_group(chunk: ms.Chunk) -> CameraGroup.Attributes:
    """Returns a bundle of camera keys, labels, flags, and sensor keys."""

    attributes: CameraGroup.Attributes = CameraGroup.Attributes()

    for camera in chunk.cameras:
        identifier: CameraID = CameraID(key=camera.key, label=camera.label)

        attributes.identifiers.append(identifier)
        attributes.image_labels[identifier] = _get_photo_label(camera.photo)
        attributes.masters[identifier] = CameraID(
            key=camera.master.key, label=camera.master.label
        )
        attributes.sensors[identifier] = SensorID(
            key=camera.sensor.key, label=camera.sensor.label
        )

    return attributes


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


def _get_photo_label(photo: ms.Photo) -> str:
    """Returns the label for the given photo."""
    return Path(photo.path).stem


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


def compute_camera_matrix(calibration: ms.Calibration) -> np.ndarray:
    """Computes the camera matrix from a ms calibration. The camera matrix
    is defined according to the OpenCV specification."""

    half_width: int = calibration.width / 2
    half_height: int = calibration.height / 2

    fx: float = calibration.f + calibration.b1
    fy: float = calibration.f

    cx: float = calibration.cx + half_width - 0.5
    cy: float = calibration.cy + half_height - 0.5

    camera_matrix: np.ndarray = np.array(
        [
            [fx, 0.0, cx],
            [0.0, fy, cy],
            [0.0, 0.0, 1.0],
        ]
    )

    return camera_matrix


def compute_distortion_vector(calibration: ms.Calibration) -> np.ndarray:
    """Computes the vector of distortion coefficients from a ms calibration.
    Distortion coefficients are ordered according to the OpenCV specification.
    """

    distortion_vector: np.ndarray = np.array(
        [
            calibration.k1,
            calibration.k2,
            calibration.p2,
            calibration.p1,
            calibration.k3,
        ]
    )

    return distortion_vector


def compute_camera_calibration(sensor: ms.Sensor) -> CameraCalibration:
    """Converts a ms sensor to a camera calibration."""

    camera_matrix: np.ndarray = compute_camera_matrix(sensor.calibration)
    distortion: np.ndarray = compute_distortion_vector(sensor.calibration)

    location: np.ndarray = vector_to_array(
        sensor.location * sensor.chunk.transform.scale
    )
    rotation: np.ndarray = matrix_to_array(sensor.rotation)

    return CameraCalibration(
        camera_matrix=camera_matrix,
        distortion=distortion,
        width=sensor.calibration.width,
        height=sensor.calibration.height,
        location=location,
        rotation=rotation,
    )
