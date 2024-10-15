"""Module for inserting common caemra into a database."""

from typing import Callable, TypeVar

import h5py
import numpy as np
import polars as pl

from ...camera import Camera
from ...collections import CameraGroup

from ...utils.result import Ok, Err, Result

from .database import H5Database


NamedBuffers = dict[str, np.ndarray]

H5_STRING_TYPE: type = h5py.string_dtype()


T: TypeVar = TypeVar("T")


BufferFun = Callable[[T], NamedBuffers]


def buffer_and_insert_into(
    storage: H5Database.Group,
    data: T,
    buffer_func: BufferFun,
) -> Result[None, str]:
    """Converts a data type to a buffer and inserts it into the storage."""

    buffers: NamedBuffers = buffer_func(data)

    try:
        for name, buffer in buffers.items():
            storage.create_dataset(name, data=buffer)
    except (OSError, IOError, TypeError, ValueError) as error:
        return Err(error)

    return Ok(None)


def insert_labels_into(
    storage: H5Database.Group, labels: list[str]
) -> Result[None, str]:
    """Inserts a collection of labels in a persistent storage group."""
    return buffer_and_insert_into(
        storage, data=labels, buffer_func=buffer_labels
    )


def insert_camera_identifiers_into(
    storage: H5Database.Group, cameras: list[Camera.Identifier]
) -> Result[None, str]:
    """Insert a collection of camera identifiers in a persistent storage group."""
    return buffer_and_insert_into(
        storage, data=cameras, buffer_func=buffer_camera_identifiers
    )


def insert_camera_attributes_into(
    storage: H5Database.Group,
    attributes: CameraGroup.Attributes,
) -> Result[None, str]:
    """Writes a group of camera attributes to a H5 group."""
    return buffer_and_insert_into(
        storage, data=attributes, buffer_func=buffer_camera_attributes
    )


def insert_camera_metadata_into(
    storage: H5Database.Group,
    metadata: CameraGroup.Metadata,
) -> Result[None, str]:
    """Insert a collection of camera metadata in a H5 storage group."""
    return buffer_and_insert_into(
        storage, data=metadata, buffer_func=buffer_camera_metadata
    )


def convert_string_buffers(buffers: NamedBuffers) -> NamedBuffers:
    """Converts buffers with numpy string type to H5 string type."""
    for name, buffer in buffers.items():
        if buffer.dtype.type is np.str_:
            buffers[name] = buffer.astype(H5_STRING_TYPE)

    return buffers


def buffer_labels(labels: list[str]) -> NamedBuffers:
    """Converts a collection of labels to a buffer."""
    buffer: np.ndarray = np.array(labels, dtype=h5py.string_dtype())
    return {"labels": buffer}


def buffer_camera_identifiers(cameras: list[Camera.Identifier]) -> NamedBuffers:
    """Converts a collection of camera identifiers to buffers."""

    df: pl.DataFrame = pl.DataFrame(
        [
            {
                "camera_keys": camera.key,
                "camera_labels": camera.label,
            }
            for camera in cameras
        ]
    )

    buffers: NamedBuffers = {
        column: df.get_column(column).to_numpy() for column in df.columns
    }

    buffers: NamedBuffers = convert_string_buffers(buffers)

    return buffers


def buffer_camera_attributes(
    attributes: CameraGroup.Attributes,
) -> NamedBuffers:
    """Converts a group of camera attributes to buffers."""

    df: pl.DataFrame = pl.DataFrame(
        [
            {
                "camera_keys": identifier.key,
                "camera_labels": identifier.label,
                "image_labels": attributes.image_labels.get(identifier),
                "master_keys": attributes.masters.get(identifier).key,
                "master_labels": attributes.masters.get(identifier).label,
                "sensor_keys": attributes.sensors.get(identifier).key,
                "sensor_labels": attributes.sensors.get(identifier).label,
            }
            for identifier in attributes.identifiers
        ]
    )

    buffers: NamedBuffers = {
        column: df.get_column(column).to_numpy() for column in df.columns
    }

    buffers: NamedBuffers = convert_string_buffers(buffers)

    return buffers


def buffer_camera_metadata(metadata: CameraGroup.Metadata) -> NamedBuffers:
    """Converts a collection of camera metadata into buffers."""

    items: list = list()
    for camera, fields in metadata.fields.items():
        data: dict = {
            "camera_keys": camera.key,
            "camera_label": camera.label,
        }

        data.update(fields)
        items.append(data)

    df: pl.DataFrame = pl.DataFrame(items)

    buffers: NamedBuffers = {
        column: df.get_column(column).to_numpy() for column in df.columns
    }

    buffers: NamedBuffers = convert_string_buffers(buffers)

    return buffers
