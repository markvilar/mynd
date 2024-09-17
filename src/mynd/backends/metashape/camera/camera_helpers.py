"""Module for camera helper functions."""

from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple, Optional

import Metashape as ms
import numpy as np

from ....api.camera import CameraBundle, StereoBundle
from ....camera import CameraCalibration, ImageLoader
from ....containers import Pair

from .image_helpers import generate_image_loader_pairs
from .reference_helpers import CameraReferenceStats, camera_reference_stats

from ..utils.math import matrix_to_array, vector_to_array


def get_camera_bundle(chunk: ms.Chunk) -> CameraBundle:
    """Returns a bundle of camera keys, labels, flags, sensor keys, and reference statistics."""

    bundle: CameraBundle = CameraBundle()

    for camera in chunk.cameras:
        bundle.keys.append(camera.key)
        bundle.labels[camera.key] = camera.label
        bundle.enabled[camera.key] = camera.enabled
        bundle.sensors[camera.key] = camera.sensor.key
        bundle.images[camera.key] = _get_photo_label(camera.photo)

        # NOTE: Get camera reference statistics
        references: Optional[CameraReferenceStats] = camera_reference_stats(camera)

        if references:
            # TODO: Convert to numpy
            bundle.aligned_locations[camera.key] = references.aligned_location
            bundle.aligned_rotations[camera.key] = references.aligned_rotation

            # TODO: Calculate prior location and rotation
            # bundle.prior_locations[camera.key] = references.prior_location
            # bundle.prior_lo

    return bundle


SensorPair = Pair[ms.Sensor]
CameraPair = Pair[ms.Camera]


class StereoGroup(NamedTuple):
    """Class representing a pair of stereo sensors and their corresponding camera pairs."""

    sensor_pair: SensorPair
    camera_pairs: list[CameraPair]


def get_stereo_bundles(chunk: ms.Chunk) -> list[StereoBundle]:
    """Composes stereo collections for the sensors and cameras in the chunk.
    Stereo collections are based on master-slave pairs of sensor and their
    corresponding cameras."""

    sensor_pairs: set[SensorPair] = _get_sensor_pairs(chunk)
    camera_pairs: set[CameraPair] = _get_camera_pairs(chunk)

    stereo_groups: list[StereoGroup] = [
        _group_stereo_cameras(sensor_pair, camera_pairs) for sensor_pair in sensor_pairs
    ]

    collections: list[StereoBundle] = list()
    for group in stereo_groups:

        calibrations: Pair[CameraCalibration] = Pair(
            first=compute_camera_calibration(group.sensor_pair.first),
            second=compute_camera_calibration(group.sensor_pair.second),
        )

        image_loaders: list[Pair[ImageLoader]] = generate_image_loader_pairs(
            group.camera_pairs
        )

        collection: StereoBundle = StereoBundle(
            calibrations=calibrations,
            image_loaders=image_loaders,
        )

        collections.append(collection)

    return collections


def _get_photo_label(photo: ms.Photo) -> str:
    """Returns the label for the given photo."""
    return Path(photo.path).stem


def _group_stereo_cameras(
    sensor_pair: SensorPair,
    camera_pairs: Iterable[CameraPair],
) -> StereoGroup:
    """Groups stereo cameras by matching the camera sensors with the sensor pair."""
    filtered_camera_pairs: list[CameraPair] = [
        camera_pair
        for camera_pair in camera_pairs
        if camera_pair.first.sensor == sensor_pair.first
        and camera_pair.second.sensor == sensor_pair.second
    ]

    return StereoGroup(sensor_pair=sensor_pair, camera_pairs=filtered_camera_pairs)


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
    Distortion coefficients are ordered according to the OpenCV specification."""

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
