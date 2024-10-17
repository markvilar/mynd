"""Module for camera helper functions."""

from pathlib import Path

import Metashape as ms
import numpy as np

from mynd.camera import Camera, CameraID, CameraCalibration, SensorID
from mynd.collections import CameraGroup

from mynd.utils.literals import literal_primitive

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


MetadataValue = str | bool | int | float


def get_camera_metadata(chunk: ms.Chunk) -> CameraGroup.Metadata:
    """Returns a metadata mapping for all the cameras in the chunk."""

    metadata: dict[CameraID, dict] = dict()
    for camera in chunk.cameras:

        camera_identifier: CameraID = CameraID(camera.key, camera.label)

        fields: dict[str, str | bool | int | float] = {
            key: literal_primitive(value) for key, value in camera.meta.items()
        }

        metadata[camera_identifier] = fields
    return CameraGroup.Metadata(metadata)


def get_camera_images(chunk: ms.Chunk) -> dict[CameraID, Path]:
    """Returns the image paths from the chunk."""
    return {
        CameraID(camera.key, camera.label): Path(camera.photo.path)
        for camera in chunk.cameras
    }


def update_camera_metadata(
    chunk: ms.Chunk, metadata: dict[str, Camera.Metadata]
) -> None:
    """Update the metadata for a collection of chunk cameras."""

    updated_cameras: dict[str, dict] = dict()
    for camera in chunk.cameras:
        if camera.label not in metadata:
            continue

        fields: dict = metadata.get(camera.label)

        for field, value in fields.items():
            # NOTE: Metashape only allows string values in camera metadata
            camera.meta[str(field)] = str(value)
        updated_cameras[camera.label] = fields


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


def _get_photo_label(photo: ms.Photo) -> str:
    """Returns the label for the given photo."""
    return Path(photo.path).stem
