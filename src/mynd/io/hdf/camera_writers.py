"""Module for inserting common caemra into a database."""

import h5py
import numpy as np
import polars as pl

from ...camera import Camera
from ...collections import CameraGroup
from ...utils.result import Ok, Err, Result

from .database import H5Database


CameraID = Camera.Identifier

STRING_TYPE: type = h5py.string_dtype()


def insert_labels_into(
    storage: H5Database.Group, labels: list[str]
) -> Result[None, str]:
    """Inserts a collection of labels in a persistent storage group."""
    labels: np.ndarray = np.array(labels, dtype=h5py.string_dtype())
    storage.create_dataset("labels", data=labels)

    return Ok(None)


def insert_camera_attributes_into(
    storage: H5Database.Group,
    attributes: CameraGroup.Attributes,
) -> Result[None, str]:
    """Writes attributes to a H5 group."""

    frame: pl.DataFrame = camera_attributes_to_data_frame(attributes)

    arrays: dict[str, np.ndarray] = {
        "camera_keys": frame.get_column("camera_key").to_numpy(),
        "camera_labels": frame.get_column("camera_label")
        .to_numpy()
        .astype(STRING_TYPE),
        "image_labels": frame.get_column("image_label")
        .to_numpy()
        .astype(STRING_TYPE),
        "master_keys": frame.get_column("master_key").to_numpy(),
        "master_labels": frame.get_column("master_label")
        .to_numpy()
        .astype(STRING_TYPE),
        "sensor_keys": frame.get_column("sensor_key").to_numpy(),
        "sensor_labels": frame.get_column("sensor_label")
        .to_numpy()
        .astype(STRING_TYPE),
    }

    try:
        for name, values in arrays.items():
            storage.create_dataset(name, data=values)

    except (OSError, IOError, TypeError, ValueError) as error:
        return Err(error)

    return Ok(None)


def insert_camera_identifiers_into(
    storage: H5Database.Group, cameras: list[CameraID]
) -> Result[None, str]:
    """Insert a collection of camera identifiers in a persistent storage group."""
    camera_keys: np.ndarray = np.array([camera.key for camera in cameras])
    camera_labels: np.ndarray = np.array(
        [camera.label for camera in cameras], dtype=STRING_TYPE
    )

    storage.create_dataset("camera_keys", data=camera_keys)
    storage.create_dataset("camera_labels", data=camera_labels)

    return Ok(None)


def camera_attributes_to_data_frame(
    attributes: CameraGroup.Attributes,
) -> pl.DataFrame:
    """Converts camera attributes to a data frame."""

    data: pl.DataFrame = pl.DataFrame(
        [
            {
                "camera_key": identifier.key,
                "camera_label": identifier.label,
                "image_label": attributes.image_labels.get(identifier),
                "master_key": attributes.masters.get(identifier).key,
                "master_label": attributes.masters.get(identifier).label,
                "sensor_key": attributes.sensors.get(identifier).key,
                "sensor_label": attributes.sensors.get(identifier).label,
            }
            for identifier in attributes.identifiers
        ]
    )

    return data
