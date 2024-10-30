"""Module for export handlers."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeAlias

from mynd.camera import CameraID, Sensor, CameraCalibration
from mynd.collections import CameraGroup, SensorImages
from mynd.image import ImageCompositeLoader

from mynd.geometry import (
    StereoRectificationResult,
    compute_stereo_rectification,
)

import h5py as h5

from mynd.io.h5 import H5Database, load_file_database, create_file_database
from mynd.io.h5 import (
    insert_camera_attributes_into,
    insert_camera_references_into,
    insert_camera_metadata_into,
)

from mynd.io.h5 import (
    insert_sensor_identifier_into,
    insert_sensor_into,
    insert_stereo_rectification_into,
)

from mynd.utils.containers import Pair
from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


StorageGroup = H5Database.Group
ErrorCallback = Callable[[str], None]


ImageCompositeLoaders: TypeAlias = Mapping[CameraID, ImageCompositeLoader]
H5Group: TypeAlias = H5Database.Group


CAMERA_STORAGE_GROUPS: list[str] = [
    "cameras",
    "references/aligned",
    "references/priors",
]


CAMERA_STORAGE_NAME: str = "cameras"
IMAGE_STORAGE_GROUP: str = "images"


@dataclass
class H5CameraStorage:
    """Class representing a storage context."""

    database: H5Database
    base: h5.Group
    attributes: h5.Group
    reference_estimates: h5.Group
    reference_priors: h5.Group
    metadata: h5.Group

    sensors: h5.Group
    stereo: h5.Group


def export_camera_database_h5(
    destination: Path,
    camera_group: CameraGroup,
    image_groups: list[SensorImages] | None = None,
    error_callback: Callable = None,
) -> Result:
    """TODO"""

    camera_storage: H5CameraStorage = initialize_storage(
        destination, camera_group
    )

    handle_camera_export(
        camera_storage, camera_group, error_callback=error_callback
    )

    camera_storage.base.visit(logger.info)

    if image_groups is not None:
        raise NotImplementedError("image export is currently not supported")


def initialize_storage(
    destination: Path, camera_group: CameraGroup
) -> H5CameraStorage:
    """Initializes storage groups by loading or creating a file database."""

    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    # Create base storage group
    base_name: str = camera_group.group_identifier.label

    base_group: h5.Group = database.create_group(base_name).unwrap()

    attributes: h5.Group = base_group.create_group("cameras/attributes")
    metadata: h5.Group = base_group.create_group("cameras/metadata")
    reference_estimates: h5.Group = base_group.create_group(
        "references/aligned"
    )
    reference_priors: h5.Group = base_group.create_group("references/prior")
    sensors: h5.Group = base_group.create_group("cameras/sensors")
    stereo: h5.Group = base_group.create_group("cameras/stereo")

    return H5CameraStorage(
        database=database,
        base=base_group,
        attributes=attributes,
        metadata=metadata,
        reference_estimates=reference_estimates,
        reference_priors=reference_priors,
        sensors=sensors,
        stereo=stereo,
    )


def handle_camera_export(
    storage: H5CameraStorage,
    cameras: CameraGroup,
    result_callback: Callable | None = None,
    error_callback: Callable | None = None,
) -> None:
    """Handles exporting of camera groups."""

    if cameras.attributes:
        result: Result[None, str] = insert_camera_attributes_into(
            storage.attributes,
            cameras.attributes,
        )

        match result:
            case Ok(None):
                logger.trace("wrote camera attributes!")
            case Err(message):
                error_callback(message)

    if cameras.reference_estimates:
        result: Result[None, str] = insert_camera_references_into(
            storage.reference_estimates,
            cameras.reference_estimates,
        )

        match result:
            case Ok(None):
                logger.trace("wrote aligned references!")
            case Err(message):
                error_callback(message)

    if cameras.reference_priors:
        result: Result[None, str] = insert_camera_references_into(
            storage.reference_priors,
            cameras.reference_priors,
        )

        match result:
            case Ok(None):
                logger.trace("wrote prior references!")
            case Err(message):
                error_callback(message)

    if cameras.metadata:
        result: Result[None, str] = insert_camera_metadata_into(
            storage.metadata,
            cameras.metadata,
        )

        match result:
            case Ok(None):
                logger.trace("wrote camera metadata!")
            case Err(message):
                error_callback(message)

    if cameras.attributes:
        for sensor in cameras.attributes.sensors:
            result: Result[None, str] = insert_sensor_into(
                storage.sensors.create_group(f"{sensor.identifier.label}"),
                sensor,
            )

            match result:
                case Ok(None):
                    logger.trace("wrote camera sensor!")
                case Err(message):
                    error_callback(message)

    if cameras.attributes:
        stereo_pairs: list[Pair[Sensor]] = cameras.attributes.stereo_sensors

        assert len(stereo_pairs) == 1, "multiple stereo pairs is not handled"

        for stereo_pair in stereo_pairs:
            calibrations: Pair[CameraCalibration] = Pair(
                stereo_pair.first.calibration,
                stereo_pair.second.calibration,
            )

            rectification: StereoRectificationResult = (
                compute_stereo_rectification(calibrations)
            )

            result: Result[None, str] = insert_sensor_identifier_into(
                storage.stereo.create_group(
                    f"sensors/{stereo_pair.first.identifier.label}"
                ),
                stereo_pair.first.identifier,
            )

            result: Result[None, str] = insert_sensor_identifier_into(
                storage.stereo.create_group(
                    f"sensors/{stereo_pair.second.identifier.label}"
                ),
                stereo_pair.second.identifier,
            )

            insert_stereo_rectification_into(
                storage.stereo.create_group("rectification"),
                rectification,
            )
