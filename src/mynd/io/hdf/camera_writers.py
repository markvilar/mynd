"""Module for inserting common caemra into a database."""

import h5py
import numpy as np

from ...camera import Camera
from ...utils.result import Ok, Result

from .database import H5Database


CameraID = Camera.Identifier


def insert_camera_identifiers_into(
    storage: H5Database.Group, cameras: list[CameraID]
) -> Result[None, str]:
    """Insert a collection of camera identifiers in a persistent storage group."""
    camera_keys: np.ndarray = np.array([camera.key for camera in cameras])
    camera_labels: np.ndarray = np.array(
        [camera.label for camera in cameras], dtype=h5py.string_dtype()
    )

    storage.create_dataset("camera_keys", data=camera_keys)
    storage.create_dataset("camera_labels", data=camera_labels)

    return Ok(None)


def insert_labels_into(
    storage: H5Database.Group, labels: list[str]
) -> Result[None, str]:
    """Inserts a collection of labels in a persistent storage group."""
    labels: np.ndarray = np.array(labels, dtype=h5py.string_dtype())
    storage.create_dataset("labels", data=labels)

    return Ok(None)
