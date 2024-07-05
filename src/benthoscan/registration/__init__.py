"""Package with registration functionality."""

from .point_cloud_types import PointCloud
from .point_cloud_loaders import PointCloudLoader, write_point_cloud, read_point_cloud

from .point_cloud_registrators import (
    MultiTargetIndex,
    downsample_point_cloud,
    estimate_point_cloud_normals,
    generate_cascade_indices,
)

from .point_cloud_registrators import (
    ExtendedRegistrationResult,
    register_point_cloud_fphp_fast,
    register_point_cloud_fphp_ransac,
    register_point_cloud_icp,
)

from .point_cloud_registrators import (
    build_pose_graph,
    optimize_pose_graph,
)
