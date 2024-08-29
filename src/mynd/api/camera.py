"""Module for camera API types."""

from typing import NamedTuple

from ..camera import CameraCalibration


class StereoData(NamedTuple):
    """Class representing stereo data."""
    
    master: CameraCalibration
    slave: CameraCalibration
    image_loaders: list

