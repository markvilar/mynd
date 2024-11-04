"""Package with functionality for registering point clouds."""

from .data_types import (
    Feature,
    RigidTransformation,
    RegistrationResult,
)

from .feature_registrators import (
    extract_fpfh_features,
    generate_correspondence_validators,
    register_features_fast,
    register_features_ransac,
    build_ransac_registrator,
)

from .full_registrators import (
    build_pose_graph,
    optimize_pose_graph,
)

from .icp_registrators import (
    register_regular_icp,
    register_colored_icp,
    build_regular_icp_registrator,
    build_colored_icp_registrator,
)

from .pipeline import RegistrationPipeline, apply_registration_pipeline

from .point_cloud_processors import (
    downsample_point_cloud,
    estimate_point_cloud_normals,
    build_point_cloud_processor,
)

from .processor_types import (
    PointCloudProcessor,
    FeatureExtractor,
    FeatureRegistrator,
    GlobalRegistrator,
    IncrementalRegistrator,
)

from .utilities import (
    MultiTargetIndex,
    generate_cascade_indices,
    log_registration_result,
)


__all__ = [
    # ...
    "Feature",
    "RigidTransformation",
    "RegistrationResult",
    # ...
    "extract_fpfh_features",
    "generate_correspondence_validators",
    "register_features_fast",
    "register_features_ransac",
    "build_ransac_registrator",
    # ...
    "build_pose_graph",
    "optimize_pose_graph",
    # ...
    "register_regular_icp",
    "register_colored_icp",
    "build_regular_icp_registrator",
    "build_colored_icp_registrator",
    # ...
    "RegistrationPipeline",
    "apply_registration_pipeline",
    # ...
    "downsample_point_cloud",
    "estimate_point_cloud_normals",
    "build_point_cloud_processor",
    # ...
    "PointCloudProcessor",
    "FeatureExtractor",
    "FeatureRegistrator",
    "GlobalRegistrator",
    "IncrementalRegistrator",
    # ...
    "MultiTargetIndex",
    "generate_cascade_indices",
    "log_registration_result",
]
