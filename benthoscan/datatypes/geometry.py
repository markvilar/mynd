""" This module contains basic geometric types. """

from dataclasses import dataclass
from typing import Optional


@dataclass
class Vec3:
    """TODO"""

    x: float
    y: float
    z: float


@dataclass
class Geolocation:
    """TODO"""

    latitude: float
    longitude: float
    height: float


@dataclass
class OrientationRPY:
    """TODO"""

    roll: float
    pitch: float
    yaw: float
