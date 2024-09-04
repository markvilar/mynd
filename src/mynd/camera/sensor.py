"""Module for camera sensors."""

from dataclasses import dataclass
from typing import Optional, Self


@dataclass
class Sensor:
    """Class representing a sensor."""

    key: int
    label: str

    master: bool
    width: int
    height: int

    fixed_location: bool = False
    fixed_rotation: bool = False

    location: Optional[list] = None
    rotation: Optional[list] = None
    location_accuracy: Optional[list] = None
    rotation_accuracy: Optional[list] = None

    bands: Optional[list[dict]] = None

    def __post_init__(self: Self) -> Self:
        """Post initialization method."""
        self.sort_index = self.key
        return self

    def __hash__(self: Self) -> Self:
        """Hash dunder method."""
        return self.key

    @property
    def size(self: Self) -> tuple[int, int]:
        """Returns the size, i.e. the width and height, of the sensor."""
        return self.width, self.height

    @property
    def has_bands(self: Self) -> bool:
        """Returns true if the sensor has assigned bands."""
        return self.bands is not None

    @property
    def has_location(self: Self) -> bool:
        """Returns true if the sensor has a location."""
        return self.location is not None

    @property
    def has_rotation(self: Self) -> bool:
        """Returns true if the sensor has a rotation."""
        return self.rotation is not None

    @property
    def has_location_accuracy(self: Self) -> bool:
        """Returns true if the sensor has a location accuracy."""
        return self.location_accuracy is not None

    @property
    def has_rotation_accuracy(self: Self) -> bool:
        """Returns true if the sensor has a rotation accuracy."""
        return self.rotation_accuracy is not None
