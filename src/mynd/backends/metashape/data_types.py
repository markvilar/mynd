"""Module for backend data types."""

from typing import NamedTuple

import Metashape


from ...containers.pair import Pair


SensorPair = Pair[Metashape.Sensor]
CameraPair = Pair[Metashape.Camera]


class StereoGroup(NamedTuple):
    """Class representing a collection of sensor and camera pairs."""

    sensor_pair: SensorPair
    camera_pairs: list[CameraPair]
