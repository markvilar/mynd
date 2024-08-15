"""Module for image and camera helper functions."""

from typing import NamedTuple

import Metashape
import numpy as np

from ...geometry.stereo import CameraCalibration, StereoCalibration, StereoExtrinsics


class SensorPair(NamedTuple):
    """Class representing a master-slave pair of sensors."""

    master: Metashape.Sensor
    slave: Metashape.Sensor


class CameraPair(NamedTuple):
    """Class representing a master-slave pair of cameras."""

    master: Metashape.Camera
    slave: Metashape.Camera


class StereoGroup(NamedTuple):
    """Class representing a collection of sensor and camera pairs."""

    sensor_pair: SensorPair
    camera_pairs: list[CameraPair]


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
            if camera_pair.master.sensor == sensor_pair.master
            and camera_pair.slave.sensor == sensor_pair.slave
        ]

        stereo_groups.append(
            StereoGroup(
                sensor_pair=sensor_pair,
                camera_pairs=selected_camera_pairs,
            )
        )

    return stereo_groups


def image_dtype_to_numpy(image: Metashape.Image) -> np.dtype:
    """Converts a Metashape image data type to a Numpy dtype."""

    match image.data_type:
        case "U8":
            return np.uint8
        case "U16":
            return np.uint16
        case "U32":
            return np.uint32
        case "U64":
            return np.uint64
        case "F16":
            return numpy.float16
        case "F32":
            return numpy.float32
        case "F64":
            return numpy.float64
        case _:
            raise NotImplementedError("unknown data type in convert_data_type_to_numpy")


def image_to_array(image: Metashape.Image) -> np.ndarray:
    """Converts a Metashape image to a Numpy array. The format of the returned image is RGB."""

    data_type: np.dtype = image_dtype_to_numpy(image)

    image_array = np.frombuffer(image.tostring(), dtype=data_type)
    assert len(image_array) == image.height * image.width * image.cn
    image_array: np.ndarray = image_array.reshape(image.height, image.width, image.cn)

    return image_array


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

    projection: np.ndarray = compute_camera_matrix(calibration)
    distortion: np.ndarray = compute_distortion_vector(calibration)

    return CameraCalibration(
        projection=projection,
        distortion=distortion,
        width=calibration.width,
        height=calibration.height,
    )


def compute_stereo_extrinsics(sensors: SensorPair) -> StereoExtrinsics:
    """Compute the relative location and rotation between two Metashape sensors."""

    location: Metashape.Vector = (
        sensors.slave.location * sensors.slave.chunk.transform.scale
    )
    rotation: Metashape.Matrix = sensors.slave.rotation

    location: np.ndarray = np.array(location)
    rotation: np.ndarray = np.array(rotation).reshape(3, 3)

    return StereoExtrinsics(location, rotation)


def compute_stereo_calibration(sensors: SensorPair) -> StereoCalibration:
    """Compute intrinsic and extrinsic calibration for a pair of Metashape sensors."""

    master: CameraCalibration = compute_camera_calibration(sensors.master.calibration)
    slave: CameraCalibration = compute_camera_calibration(sensors.slave.calibration)

    extrinsics: StereoExtrinsics = compute_stereo_extrinsics(sensors)

    return StereoCalibration(master=master, slave=slave, extrinsics=extrinsics)
