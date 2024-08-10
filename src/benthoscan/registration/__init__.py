"""Package with registration functionality."""

from .data_types import (
    PointCloud,
    Feature,
    RigidTransformation,
    RegistrationResult,
)

from .feature_registrators import (
    extract_fpfh_features,
    generate_correspondence_validators,
    register_features_fast,
    register_features_ransac,
)

from .incremental_registrators import (
    register_icp,
    register_colored_icp,
    build_pose_graph,
    optimize_pose_graph,
)

from .pipeline import (
    Module,
    ModuleList,
    apply_registration_modules,
)

from .point_cloud_loaders import (
    PointCloudLoader,
    read_point_cloud,
    create_point_cloud_loader,
)

from .point_cloud_processors import (
    downsample_point_cloud,
    estimate_point_cloud_normals,
)

from .processor_types import (
    PointCloudProcessor,
    FeatureExtractor,
    FeatureRegistrator,
    GlobalRegistrator,
    IncrementalRegistrator,
)

from .registration_utilities import (
    MultiTargetIndex,
    generate_cascade_indices,
)

from .registrator_builders import (
    ComponentBuildData,
    ComponentBuildResult,
    build_point_cloud_processor,
    build_feature_registrator,
    build_icp_registrator,
    build_components_and_compose,
)
