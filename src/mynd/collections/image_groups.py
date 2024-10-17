"""Module for various image collections."""

from dataclasses import dataclass
from typing import Self

from ..camera import CameraID, SensorID
from ..image import ImageCompositeLoader


@dataclass
class SensorImages:
    """Class representing a group of image data captured by a sensor."""

    sensor: SensorID
    loaders: dict[CameraID, ImageCompositeLoader]

    @property
    def cameras(self: Self) -> list[CameraID]:
        """The foo property."""
        return list(self.loaders.keys())
