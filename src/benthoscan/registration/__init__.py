"""Package with registration functionality."""

from .point_cloud_types import PointCloud
from .point_cloud_loaders import PointCloudLoader, write_point_cloud, read_point_cloud

from .point_cloud_processors import (
    downsample_point_cloud,
    estimate_point_cloud_normals,
)

from .point_cloud_registrators import (
    register_point_cloud_fphp_fast,
    register_point_cloud_fphp_ransac,
    register_point_cloud_icp,
    build_pose_graph,
    optimize_pose_graph,
)

from .registration_types import (
    ExtendedRegistrationResult,
    GlobalRegistrator,
    IncrementalRegistrator,
)

from .registration_utilities import (
    MultiTargetIndex,
    generate_cascade_indices,
)
