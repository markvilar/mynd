"""Module for camera references."""

from dataclasses import dataclass
from typing import Optional, Self


@dataclass
class CameraReference:
    """Class representing a camera reference."""

    location: Optional[list] = None
    rotation: Optional[list] = None

    def has_location(self: Self) -> bool:
        """Returns true if the reference has a location."""
        return self.location is not None

    def has_rotation(self: Self) -> bool:
        """Returns true if the reference has a rotation."""
        return self.rotation is not None
