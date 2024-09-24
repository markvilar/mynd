"""Module for camera API types."""

from dataclasses import dataclass, field

from ..camera import CameraCalibration, ImageLoader
from ..containers import Pair


@dataclass
class CameraAttributeGroup:
    """Class representing a group of camera attributes."""

    keys: list[int] = field(default_factory=list)
    labels: dict[int, str] = field(default_factory=dict)
    image_labels: dict[int, str] = field(default_factory=dict)
    master_keys: dict[int, int] = field(default_factory=dict)
    sensor_keys: dict[int, int] = field(default_factory=dict)


@dataclass
class CameraReferenceGroup:
    """Class representing a group of camera references."""

    keys: list[int] = field(default_factory=list)
    locations: dict[int, list] = field(default_factory=dict)
    rotations: dict[int, list] = field(default_factory=dict)


@dataclass
class StereoCameraGroup:
    """Class representing a stereo camera group."""

    # TODO: Add sensors
    # TODO: Add camera keys
    calibrations: Pair[CameraCalibration]
    image_loaders: list[Pair[ImageLoader]]
