"""Moduel for inserting sensors into a database."""

from mynd.camera import Sensor, CameraCalibration

from .database import H5Database


def insert_sensor_identifier_into(
    storage: H5Database.Group, identifier: Sensor.Identifier
) -> None:
    """Inserts a sensor identifier into a storage group."""
    storage.create_dataset("key", data=identifier.key, shape=(1,))
    storage.create_dataset("label", data=identifier.label, shape=(1,))


def insert_sensor_into(storage: H5Database.Group, sensor: Sensor) -> None:
    """Insert a sensor into a storage group."""
    storage.create_dataset("key", data=sensor.identifier.key, shape=(1,))
    storage.create_dataset("label", data=sensor.identifier.label, shape=(1,))
    storage.create_dataset("width", data=sensor.width, shape=(1,))
    storage.create_dataset("height", data=sensor.height, shape=(1,))

    # TODO: Add sensor reference
    # TODO: Add sensor bands

    if sensor.calibration:
        insert_calibration_into(
            storage.create_group("calibration"), sensor.calibration
        )

    if sensor.master:
        storage.create_dataset("master_key", data=sensor.master.key, shape=(1,))
        storage.create_dataset(
            "master_label", data=sensor.master.label, shape=(1,)
        )


def insert_calibration_into(
    group: H5Database.Group, calibration: CameraCalibration
) -> None:
    """Adds a camera calibration to a file database group."""

    group.create_dataset("width", data=calibration.width, shape=(1,))
    group.create_dataset("height", data=calibration.height, shape=(1,))
    group.create_dataset("camera_matrix", data=calibration.camera_matrix)
    group.create_dataset("distortion", data=calibration.distortion)
    group.create_dataset("location", data=calibration.location)
    group.create_dataset("rotation", data=calibration.rotation)
