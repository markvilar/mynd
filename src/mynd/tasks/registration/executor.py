"""Module for executing registration tasks."""

from ...registration import PointCloudLoader
from ...utils.result import Err, Result

from .config_types import RegistrationTaskConfig


def execute_point_cloud_registration(
    config: RegistrationTaskConfig,
) -> Result[None, str]:
    """Executes a point cloud registration task."""

    loaders: dict[int, PointCloudLoader] = config.point_cloud_loaders

    count = len(loaders)
    if count < 2:
        return Err(f"invalid number of point clouds for registration: {count}")

    # TODO: Set up registration schema
    # TODO: Build registration processes
    # TODO: Run registration processes

    return Err("execute_point_cloud_registration is not implemented")
