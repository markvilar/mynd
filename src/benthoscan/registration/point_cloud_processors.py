"""Module for point cloud processors."""

from copy import deepcopy

import open3d.geometry as geom

from .data_types import PointCloud


def downsample_point_cloud(
    cloud: PointCloud,
    spacing: float,
    inplace: bool = False,
) -> PointCloud:
    """Downsamples a point cloud by performing voxel resampling."""
    if not inplace:
        cloud = deepcopy(cloud)

    cloud = cloud.voxel_down_sample(voxel_size=spacing)
    return cloud


def estimate_point_cloud_normals(
    cloud: PointCloud,
    radius: float = 0.10,
    neighbours: int = 30,
    inplace: bool = False,
) -> PointCloud:
    """Estimates the normals of a point cloud based on neighbouring points."""
    if not inplace:
        cloud = deepcopy(cloud)

    cloud.estimate_normals(
        search_param=geom.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
    )
    return cloud
