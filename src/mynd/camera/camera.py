"""Module for camera data."""

from dataclasses import dataclass
from typing import Optional, TypeAlias

from .sensor import Sensor


@dataclass(frozen=True)
class Camera:
    """Class representing a camera composition."""

    @dataclass(frozen=True)
    class Identifier:
        """Class representing a camera identifier."""

        key: int
        label: Optional[str] = None

    identifier: Identifier
    sensor: Sensor.Identifier


Metadata: TypeAlias = dict[str, int | float | bool | str]
