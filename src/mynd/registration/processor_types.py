"""Module for point cloud registrators, including global, incremental, and full registrators."""

from collections.abc import Callable

from ..geometry import PointCloud

from .data_types import Feature, RigidTransformation, RegistrationResult


PointCloudProcessor = Callable[[PointCloud], PointCloud]


FeatureExtractor = Callable[[PointCloud], Feature]


FeatureRegistrator = Callable[
    [PointCloud, PointCloud, Feature, Feature], RegistrationResult
]


GlobalRegistrator = Callable[[PointCloud, PointCloud], RegistrationResult]


IncrementalRegistrator = Callable[
    [PointCloud, PointCloud, RigidTransformation], RegistrationResult
]
