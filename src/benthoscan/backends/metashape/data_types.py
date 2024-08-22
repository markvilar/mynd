"""Module for backend data types."""

from typing import NamedTuple

import Metashape
import numpy as np


class SensorPair(NamedTuple):
    """Class representing a master-slave pair of sensors."""

    first: Metashape.Sensor
    second: Metashape.Sensor


class CameraPair(NamedTuple):
    """Class representing a master-slave pair of cameras."""

    first: Metashape.Camera
    second: Metashape.Camera


class StereoGroup(NamedTuple):
    """Class representing a collection of sensor and camera pairs."""

    sensor_pair: SensorPair
    camera_pairs: list[CameraPair]
