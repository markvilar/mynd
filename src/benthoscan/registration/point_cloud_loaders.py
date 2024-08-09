"""Module for point cloud IO, i.e. reading and writing point clouds."""

from collections.abc import Callable
from pathlib import Path

import open3d

from result import Ok, Err, Result

from .data_types import PointCloud


PointCloudLoader = Callable[[None], Result[PointCloud, str]]


def read_point_cloud(path: str | Path) -> Result[PointCloud, str]:
    """Loads a point cloud from a file."""

    try:
        point_cloud: PointCloud = open3d.io.read_point_cloud(str(path))
        return Ok(point_cloud)
    except IOError as error:
        return Err(str(error))


def create_point_cloud_loader(source: str | Path) -> PointCloudLoader:
    """Creates a point cloud loader for the given source."""

    def wrapper() -> Result[PointCloud, str]:
        """Loads a point cloud."""
        return read_point_cloud(path=source)

    return wrapper
