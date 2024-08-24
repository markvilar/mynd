"""Module for spatial transformations."""

import numpy as np

from scipy.spatial.transform import Rotation


def decompose_transformation(transformation: np.ndarray) -> tuple:
    """Decomposes a 3D rigid body transformation into scale, rotation, and translation."""

    assert transformation.shape == (
        4,
        4,
    ), "transformation is not a 3D rigid-body transformation"

    scaled_rotation: np.ndarray = transformation[:3, :3]
    translation: np.ndarray = transformation[:3, 3]

    scale: float = np.linalg.norm(scaled_rotation, axis=1)[0]
    rotation: np.ndarray = scaled_rotation / scale

    return scale, rotation, translation


def decompose_rotation(rotation: np.ndarray) -> tuple:
    """Decomposes a 3D rotation matrix into yaw, roll, and pitch angles."""

    assert rotation.shape == (
        3,
        3,
    ), "rotation is not a 3D rotation matrix"

    rotation: Rotation = Rotation.from_matrix(rotation)

    yaw, roll, pitch = rotation.as_euler("ZYX", degrees=True)

    return yaw, roll, pitch
