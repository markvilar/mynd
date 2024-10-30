"""Module for camera calibrations."""

from dataclasses import dataclass
from typing import Self

import numpy as np


@dataclass
class CameraCalibration:
    """Class representing a camera calibration."""

    camera_matrix: np.ndarray
    distortion: np.ndarray
    width: int
    height: int

    # TODO: Consider moving location and rotation to sensor class
    location: np.ndarray
    rotation: np.ndarray

    @property
    def focal_length(self: Self) -> float:
        """Returns the focal length from a camera calibration."""
        return self.camera_matrix[0, 0]

    @property
    def optical_center(self: Self) -> tuple[float, float]:
        """Returns the optical center for the camera calibration."""
        return (self.camera_matrix[0, 2], self.camera_matrix[1, 2])

    @property
    def image_size(self: Self) -> tuple[int, int]:
        """Returns the image size as height, width."""
        return (self.height, self.width)

    @property
    def baseline(self: Self) -> float:
        """Returns the baseline of the calibration."""
        return np.linalg.norm(self.location)
