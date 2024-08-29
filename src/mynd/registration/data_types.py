"""Module for registration data types."""

from dataclasses import dataclass

import numpy as np
import open3d


Feature = open3d.pipelines.registration.Feature


RigidTransformation = np.ndarray


@dataclass
class RegistrationResult:
    """Class representing registration results including the information matrix."""

    fitness: float
    inlier_rmse: float
    correspondence_set: np.ndarray
    transformation: np.ndarray
    information: np.ndarray
