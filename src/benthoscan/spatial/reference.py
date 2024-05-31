"""Module for camera references."""

from dataclasses import dataclass
from typing import Optional

from .geometry import Vec3


@dataclass
class ReferenceSettings:
    """Class representing reference settings."""

    @dataclass
    class Accuracies:
        """Class representing reference accuracies."""

        position: Vec3
        orientation: Vec3

    @dataclass
    class Formats:
        """Class representing reference formats."""

        position: str = "WGS84"
        orientation: str = "YPR"


    group: str
    accuracies: Accuracies
    formats: Formats
    

@dataclass
class SpatialReference:
    """Class representing a spatial reference."""

    position: Optional[Vec3] = None
    orientation: Optional[Vec3] = None
    position_accuracy: Optional[Vec3] = None
    orientation_accuracy: Optional[Vec3] = None

    @property
    def has_position(self) -> bool:
        """Returns true if the camera reference has a position component."""
        return not self.position is None

    @property
    def has_position_accuracy(self) -> bool:
        """Returns true if the camera reference has a position accuracy
        component."""
        return not self.position_accuracy is None

    @property
    def has_orientation(self) -> bool:
        """Returns true if the camera reference has a orienation component."""
        return not self.orientation is None

    @property
    def has_orientation_accuracy(self) -> bool:
        """Returns true if the camera reference has orientation accuracy
        component."""
        return not self.orientation_accuracy is None

