"""Interface class for cameras."""

from dataclasses import dataclass, field
from typing import Callable, Optional, TypeAlias


@dataclass
class MonocularCamera:
    """Class representing a monocular camera."""

    label: str


@dataclass
class StereoCamera:
    """Class representing a stereo camera."""

    master: str
    slave: str


Camera = MonocularCamera | StereoCamera


@dataclass
class CameraGroup:
    """Class representing a group of cameras. The cameras in a camera group
    are assumed to be capture by the same camera setup."""

    group_name: str
    cameras: list[Camera]
