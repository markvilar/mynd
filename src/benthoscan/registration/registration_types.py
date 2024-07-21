"""Module for point cloud processors, i.e. including filters for spacing and confidence."""

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .point_cloud_types import PointCloud


@dataclass
class ExtendedRegistrationResult:
    """Class representing registration results in addition to the information matrix."""

    fitness: float
    inlier_rmse: float
    correspondence_set: np.ndarray
    transformation: np.ndarray
    information: np.ndarray


Transformation = np.ndarray


GlobalRegistrator = Callable[[PointCloud, PointCloud], ExtendedRegistrationResult]


IncrementalRegistrator = Callable[
    [PointCloud, PointCloud, Transformation], ExtendedRegistrationResult
]
