"""Module for stereo camera rigs."""

from dataclasses import dataclass

from mynd.utils.containers import Pair

from .sensor import Sensor


@dataclass
class StereoRig:
    """Class representing a stereo rig."""

    sensors: Pair[Sensor]
