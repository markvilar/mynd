"""Package with spatial functionality."""

from .point_cloud_types import PointCloud
from .point_cloud_loaders import PointCloudLoader, write_point_cloud, read_point_cloud

from .point_cloud_registrators import (
    downsample_point_cloud,
    estimate_point_cloud_normals,
    generate_cascade_indices,
)

from .point_cloud_registrators import (
    ExtendedRegistrationResult,
    register_point_cloud_fphp_fast,
    register_point_cloud_fphp_ransac,
    register_point_cloud_icp,
    register_point_cloud_pair,
    register_point_cloud_graph,
)

from .reference_types import (
    Vec3,
    Identifier,
    Geolocation,
    Orientation,
    SpatialReference,
)

from .reference_builders import build_references_from_dataframe
