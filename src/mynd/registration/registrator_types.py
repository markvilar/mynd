"""Module for point cloud registrators, including global, incremental, and full registrators."""

from collections.abc import Callable

from ..geometry import PointCloud

from .data_types import Feature, RigidTransformation, RegistrationResult


FeatureExtractor = Callable[[PointCloud], Feature]


FeatureMatcher = Callable[
    [PointCloud, PointCloud, Feature, Feature], RegistrationResult
]


PointCloudAligner = Callable[[PointCloud, PointCloud], RegistrationResult]


PointCloudRefiner = Callable[
    [PointCloud, PointCloud, RigidTransformation], RegistrationResult
]
