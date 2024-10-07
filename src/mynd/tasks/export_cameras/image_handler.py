"""Module for handling export of image groups."""

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Callable, Optional

from ...camera import Camera, Sensor
from ...collections import CameraGroup, SensorImages
from ...image import ImageBundleLoader

from ...io.h5 import H5Database
from ...io.h5 import (
    insert_image_bundles_into,
    insert_camera_identifiers_into,
    insert_labels_into,
)

from ...utils.log import logger
from ...utils.result import Ok, Err, Result

from .bundle_factories import generate_image_bundle_loaders


CameraID = Camera.Identifier
SensorID = Sensor.Identifier

ImageBundleLoaders = Mapping[CameraID, ImageBundleLoader]

ErrorCallback = Callable[[str], None]

IMAGE_BUNDLE_COMPONENTS: list[str] = ["colors", "ranges", "normals"]


def handle_image_export(
    storage: H5Database.Group,
    cameras: CameraGroup.Attributes,
    images: Mapping[str, Iterable[Path]],
    error_callback: ErrorCallback = lambda message: None,
) -> None:
    """Handles exporting of image groups."""

    assert all(
        [component in images for component in IMAGE_BUNDLE_COMPONENTS]
    ), "missing image components"

    loaders: dict[str, ImageBundleLoader] = generate_image_bundle_loaders(
        images.get("colors"),
        images.get("ranges"),
        images.get("normals"),
    )

    loaders: dict[CameraID, ImageBundleLoader] = map_loaders_to_cameras(
        cameras.image_labels, loaders
    )

    sensor_image_groups: list[SensorImages] = collect_sensor_images(
        camera_sensors=cameras.sensors,
        image_labels=cameras.image_labels,
        bundle_loaders=loaders,
    )

    log_sensor_images(sensor_image_groups)

    for sensor_images in sensor_image_groups:

        if sensor_images.sensor.label:
            storage_group_name: str = sensor_images.sensor.label
        else:
            storage_group_name: str = f"sensor_{sensor_images.sensor.key}"

        if storage_group_name in storage:
            storage_group: Optional[H5Database.Group] = storage.get(
                storage_group_name
            )
        else:
            storage_group: H5Database.Group = storage.create_group(
                storage_group_name
            )

        match insert_sensor_images_into(
            storage=storage_group, sensor_images=sensor_images
        ):
            case Ok(None):
                logger.info(
                    f"Successfully inserted sensor images: {storage_group_name}"
                )
            case Err(message):
                error_callback(message)


def log_sensor_images(sensor_image_groups: list[SensorImages]) -> None:
    """Logs an overview of groups of sensor images."""

    for sensor_images in sensor_image_groups:
        logger.info("")
        logger.info(
            f"Sensor images:    {sensor_images.sensor.key}, {sensor_images.sensor.label}"
        )
        logger.info(f"  Cameras:        {len(sensor_images.cameras)}")
        logger.info(f"  Labels:         {len(sensor_images.labels)}")
        logger.info(f"  Loaders:        {len(sensor_images.loaders)}")
        logger.info("")


def insert_sensor_images_into(
    storage: H5Database.Group,
    sensor_images: SensorImages,
) -> Result[None, str]:
    """Insert a group images into a storage group."""

    # We create lists of data members since they are order preserving
    cameras: list[CameraID] = sorted(
        sensor_images.cameras, key=lambda item: item.key
    )
    labels: list[str] = [sensor_images.labels.get(camera) for camera in cameras]
    loaders: list[ImageBundleLoader] = [
        sensor_images.loaders.get(camera) for camera in cameras
    ]

    invalid_labels: list[bool] = [label is None for label in labels]
    invalid_loaders: list[bool] = [loader is None for loader in loaders]

    if any(invalid_labels):
        return Err(f"missing {sum(invalid_labels)} labels for cameras")
    if any(invalid_loaders):
        return Err(f"missing {sum(invalid_loaders)} loaders for cameras")

    storage.attrs["sensor_key"] = sensor_images.sensor.key
    storage.attrs["sensor_label"] = sensor_images.sensor.label

    # Insert the sensor image components into the storage
    insert_results: list[Result[None, str]] = [
        insert_camera_identifiers_into(storage, cameras),
        insert_labels_into(storage, labels),
        insert_image_bundles_into(storage, loaders),
    ]

    for result in insert_results:
        if result.is_err():
            return result

    return Ok(None)


def collect_sensor_images(
    camera_sensors: dict[CameraID, SensorID],
    image_labels: dict[CameraID, str],
    bundle_loaders: ImageBundleLoaders,
) -> list[SensorImages]:
    """Collects image data into groups captured by the same sensor."""

    sensor_to_cameras: dict[SensorID, CameraID] = map_sensors_to_cameras(
        camera_sensors
    )

    sensor_image_groups: list[SensorImages] = list()
    for sensor, cameras in sensor_to_cameras.items():

        filtered_labels: dict[CameraID, str] = {
            camera: image_labels.get(camera)
            for camera in cameras
            if camera in image_labels
        }

        filtered_loaders: dict[CameraID, ImageBundleLoader] = {
            camera: bundle_loaders.get(camera)
            for camera in cameras
            if camera in bundle_loaders
        }

        sensor_image_groups.append(
            SensorImages(
                sensor=sensor,
                cameras=cameras,
                labels=filtered_labels,
                loaders=filtered_loaders,
            )
        )

    return sensor_image_groups


def map_sensors_to_cameras(
    camera_to_sensor: Mapping[CameraID, SensorID],
) -> dict[SensorID, list[str]]:
    """Creates a mapping from sensors to labels of images captured with the sensor."""
    sensor_to_cameras: dict[SensorID, list[CameraID]] = dict()
    for camera, sensor in camera_to_sensor.items():
        if sensor not in sensor_to_cameras:
            sensor_to_cameras[sensor] = list()

        sensor_to_cameras[sensor].append(camera)

    return sensor_to_cameras


def map_loaders_to_cameras(
    labels: Mapping[CameraID, str],
    loaders: Mapping[str, ImageBundleLoader],
) -> dict[CameraID, ImageBundleLoader]:
    """Maps cameras to loaders by matching image labels to the loader labels."""

    remapped_loaders: dict[CameraID, ImageBundleLoader] = {
        identifier: loaders.get(label) for identifier, label in labels.items()
    }

    return remapped_loaders
