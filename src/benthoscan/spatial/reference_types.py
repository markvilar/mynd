"""Module for spatial reference types."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Vec3:
    """Class representing a 3D vector."""

    x: float
    y: float
    z: float


@dataclass
class Identifier:
    """Class representing an Identifier."""

    label: str


@dataclass
class Geolocation:
    """Class representing a geolocation."""
    
    longitude: float
    latitude: float
    height: float


@dataclass
class Orientation:
    """Class representing an orientation."""

    roll: float
    pitch: float
    heading: float
    

@dataclass
class SpatialReference:
    """Class representing a spatial reference."""

    identifier: Identifier
    geolocation: Geolocation
    orientation: Orientation

    geolocation_accuracy: Optional[Vec3] = None
    orientation_accuracy: Optional[Vec3] = None

    @property
    def has_geolocation_accuracy(self) -> bool:
        """TODO"""
        return isinstance(self.geolocation_accuracy, Vec3)

    @property
    def has_orientation_accuracy(self) -> bool:
        """TODO"""
        return isinstance(self.orientation_accuracy, Vec3)
