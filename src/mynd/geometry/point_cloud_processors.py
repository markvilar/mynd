"""Module for point cloud processors."""

from copy import deepcopy

import open3d.geometry as geom

from .point_cloud import PointCloud, PointCloudProcessor


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


def create_downsampler(
    spacing: float,
    inplace: bool = False,
) -> PointCloudProcessor:

    def downsampler_wrapper(
        cloud: PointCloud,
    ) -> PointCloud:
        """Wraps a point cloud downsampler."""
        return downsample_point_cloud(
            cloud=cloud, spacing=spacing, inplace=inplace
        )

    return downsampler_wrapper


def create_normal_estimator(
    radius: float = 0.10,
    neighbours: int = 30,
    inplace: bool = False,
) -> PointCloudProcessor:

    def normal_estimator_wrapper(cloud: PointCloud) -> PointCloud:
        """Wraps a point cloud normal estimator."""
        return estimate_point_cloud_normals(
            cloud=cloud,
            radius=radius,
            neighbours=neighbours,
            inplace=inplace,
        )

    return normal_estimator_wrapper
