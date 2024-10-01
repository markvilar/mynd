"""Module for various image collections."""

from dataclasses import dataclass

from ..camera import Camera, Sensor
from ..image import ImageBundleLoader


CameraID = Camera.Identifier
SensorID = Sensor.Identifier


@dataclass
class SensorImages:
    """Class representing a group of image data captured by a sensor."""

    sensor: SensorID
    cameras: list[CameraID]
    labels: dict[CameraID, str]
    loaders: dict[CameraID, ImageBundleLoader]
