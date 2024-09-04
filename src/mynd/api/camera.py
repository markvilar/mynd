"""Module for camera API types."""

from dataclasses import dataclass

from ..camera import CameraCalibration, ImageLoader
from ..containers import Pair


@dataclass
class StereoCollection:
    """Class representing stereo data."""

    # TODO: Add sensors
    calibrations: Pair[CameraCalibration]
    image_loaders: list[Pair[ImageLoader]]
