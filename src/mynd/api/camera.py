"""Module for camera API types."""

from dataclasses import dataclass, field

import numpy as np

from ..camera import CameraCalibration, ImageLoader
from ..containers import Pair


@dataclass
class CameraIndexGroup:
    """Class representing a group of camera indices."""

    keys: list[int] = field(default_factory=list)
    labels: dict[int, str] = field(default_factory=dict)
    sensors: dict[int, int] = field(default_factory=dict)
    images: dict[int, str] = field(default_factory=dict)


@dataclass
class CameraReferenceGroup:
    """Class representing a group of camera references."""

    # TODO: Replace numpy arrays with data structures
    aligned_locations: dict[int, np.ndarray] = field(default_factory=dict)
    aligned_rotations: dict[int, np.ndarray] = field(default_factory=dict)

    prior_locations: dict[int, np.ndarray] = field(default_factory=dict)
    prior_rotations: dict[int, np.ndarray] = field(default_factory=dict)

    # TODO: Add location and rotation priors, errors, and covariance


@dataclass
class StereoGroup:
    """Class representing a stereo bundle."""

    # TODO: Add sensors
    calibrations: Pair[CameraCalibration]
    image_loaders: list[Pair[ImageLoader]]
