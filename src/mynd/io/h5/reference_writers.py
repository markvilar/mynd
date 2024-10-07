"""Module for inserting camera references into a HDF5 database."""

import h5py
import numpy as np
import polars as pl

from ...collections import CameraGroup
from ...utils.result import Ok, Err, Result

from .database import H5Database

STRING_TYPE = h5py.string_dtype()


def reference_group_to_data_frame(
    references: CameraGroup.References,
) -> pl.DataFrame:
    """Converts a camera refrence group to a data frame."""

    references: pl.DataFrame = pl.DataFrame(
        [
            {
                "camera_key": identifier.key,
                "camera_label": identifier.label,
                "location": references.locations.get(identifier),
                "rotation": references.rotations.get(identifier),
            }
            for identifier in references.identifiers
        ]
    )

    return references


def insert_camera_references_into(
    group: H5Database.Group,
    references: CameraGroup.References,
) -> Result[None, str]:
    """Inserts camera references into a database group."""

    frame: pl.DataFrame = reference_group_to_data_frame(references)

    # Lists in polars converts to objects in numpy, hence we need to use
    # np.stack to get the components
    arrays: dict[str, np.ndarray] = {
        "camera_keys": frame.get_column("camera_key").to_numpy(),
        "camera_labels": frame.get_column("camera_label")
        .to_numpy()
        .astype(STRING_TYPE),
        "locations": np.stack(frame.get_column("location").to_numpy()),
        "rotations": np.stack(frame.get_column("rotation").to_numpy()),
    }

    try:
        for name, values in arrays.items():
            group.create_dataset(name, data=values)

    except (OSError, IOError, TypeError, ValueError) as error:
        return Err(error)

    return Ok(None)
