"""Interface class for cameras."""

#from dataclasses import dataclass
from typing import NamedTuple, Optional, Self

#import numpy as np


# CameraLabel = str


#@dataclass(eq=True, frozen=True)
class Sensor(NamedTuple):
    """Class representing a frame sensor."""

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

#    def __init__(
#        self: Self,
#        key: int,
#        label: str,
#        master: bool,
#        width: int,
#        height: int,
#        fixed_location: bool = False,
#        fixed_rotation: bool = False,
#        location: Optional[list] = None,
#        rotation: Optional[list] = None,
#        location_accuracy: Optional[list] = None,
#        rotation_accuracy: Optional[list] = None,
#        bands: Optional[list[dict]] = None,
#    ) -> Self:
#        """Initialization method."""
#
#        object.__setattr__(self, "key", key)
#        object.__setattr__(self, "label", label)
#        object.__setattr__(self, "master", master)
#        object.__setattr__(self, "width", width)
#        object.__setattr__(self, "height", height)
#        object.__setattr__(self, "fixed_location", fixed_location)
#        object.__setattr__(self, "fixed_rotation", fixed_rotation)
#
#        object.__setattr__(self, "location", location)
#        object.__setattr__(self, "rotation", rotation)
#        object.__setattr__(self, "location_accuracy", location_accuracy)
#        object.__setattr__(self, "rotation_accuracy", rotation_accuracy)
#        object.__setattr__(self, "bands", bands)

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
