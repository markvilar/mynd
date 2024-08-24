"""Module for camera helper functions."""

import Metashape
import numpy as np

from ...data.image import Image, ImageFormat
from ...geometry.stereo import CameraCalibration, StereoCalibration, StereoExtrinsics
from ...geometry.range_maps import compute_normals_from_range

from .data_types import SensorPair, CameraPair, StereoGroup
from .image_helpers import convert_image


def get_sensor_pairs(chunk: Metashape.Chunk) -> set[SensorPair]:
    """Gets master-slave pairs of sensors from a Metashape chunk."""
    stereo_sensors: set[SensorPair] = set(
        [
            SensorPair(sensor.master, sensor)
            for sensor in chunk.sensors
            if sensor.master != sensor
        ]
    )
    return stereo_sensors


def get_camera_pairs(chunk: Metashape.Chunk) -> set[CameraPair]:
    """Gets master-slave pairs of cameras from a Metashape chunk."""
    stereo_cameras: set[CameraPair] = set(
        [
            CameraPair(camera.master, camera)
            for camera in chunk.cameras
            if camera.master != camera
        ]
    )
    return stereo_cameras


def get_stereo_groups(chunk: Metashape.Chunk) -> list[StereoGroup]:
    """Gets stereo groups, i.e. corresponding sensor and camera pairs, from a Metashape chunk."""
    sensor_pairs: set[SensorPair] = get_sensor_pairs(chunk)
    camera_pairs: set[CameraPair] = get_camera_pairs(chunk)

    stereo_groups: list[StereoGroup] = list()

    for sensor_pair in sensor_pairs:
        selected_camera_pairs: list[CameraPair] = [
            camera_pair
            for camera_pair in camera_pairs
            if camera_pair.first.sensor == sensor_pair.first
            and camera_pair.second.sensor == sensor_pair.second
        ]

        stereo_groups.append(
            StereoGroup(
                sensor_pair=sensor_pair,
                camera_pairs=selected_camera_pairs,
            )
        )

    return stereo_groups


def compute_camera_matrix(calibration: Metashape.Calibration) -> np.ndarray:
    """Computes the camera matrix from a Metashape calibration. The camera matrix
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


def compute_distortion_vector(calibration: Metashape.Calibration) -> np.ndarray:
    """Computes the vector of distortion coefficients from a Metashape calibration.
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


def compute_camera_calibration(calibration: Metashape.Calibration) -> CameraCalibration:
    """Converts a Metashape calibration to a camera calibration."""

    camera_matrix: np.ndarray = compute_camera_matrix(calibration)
    distortion: np.ndarray = compute_distortion_vector(calibration)

    return CameraCalibration(
        camera_matrix=camera_matrix,
        distortion=distortion,
        width=calibration.width,
        height=calibration.height,
    )


def compute_stereo_extrinsics(sensors: SensorPair) -> StereoExtrinsics:
    """Compute the relative location and rotation between two Metashape sensors."""

    location: Metashape.Vector = (
        sensors.second.location * sensors.second.chunk.transform.scale
    )
    rotation: Metashape.Matrix = sensors.second.rotation

    location: np.ndarray = np.array(location)
    rotation: np.ndarray = np.array(rotation).reshape(3, 3)

    return StereoExtrinsics(location, rotation)


def compute_stereo_calibration(sensors: SensorPair) -> StereoCalibration:
    """Compute intrinsic and extrinsic calibration for a pair of Metashape sensors."""

    master: CameraCalibration = compute_camera_calibration(sensors.first.calibration)
    slave: CameraCalibration = compute_camera_calibration(sensors.second.calibration)

    extrinsics: StereoExtrinsics = compute_stereo_extrinsics(sensors)

    return StereoCalibration(master=master, slave=slave, extrinsics=extrinsics)


def render_range_and_normal_maps(camera: Metashape.Camera) -> tuple[Image, Image]:
    """Render range and normal map for a Metashape camera."""

    if camera.chunk.transform.scale:
        scale: float = camera.chunk.transform.scale
    else:
        scale: float = 1.0

    range_map: Metashape.Image = camera.chunk.model.renderDepth(
        camera.transform, camera.sensor.calibration, add_alpha=False
    )

    range_map: Metashape.Image = scale * range_map
    range_map: Metashape.Image = range_map.convert(" ", "F32")

    # Compute a camera calibration and range array to calculate the normal map
    calibration: CameraCalibration = compute_camera_calibration(
        camera.sensor.calibration
    )
    range_map: Image = convert_image(range_map)
    range_map.format = ImageFormat.X

    normals: np.ndarray = compute_normals_from_range(
        range_map.data,
        camera_matrix=calibration.camera_matrix,
        flipped=True,
    )

    normal_map: Image = Image(data=normals, format=ImageFormat.XYZ)

    return range_map, normal_map
