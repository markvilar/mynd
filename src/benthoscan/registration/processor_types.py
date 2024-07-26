"""Module for point cloud registrators, including global, incremental, and full registrators."""

# from typing import Callable
from collections.abc import Callable

from .data_types import Feature, PointCloud, RigidTransformation, RegistrationResult


PointCloudProcessor = Callable[[PointCloud], PointCloud]


FeatureExtractor = Callable[[PointCloud], Feature]


FeatureRegistrator = Callable[
    [PointCloud, PointCloud, Feature, Feature], RegistrationResult
]


GlobalRegistrator = Callable[[PointCloud, PointCloud], RegistrationResult]


IncrementalRegistrator = Callable[
    [PointCloud, PointCloud, RigidTransformation], RegistrationResult
]
