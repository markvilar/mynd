"""Package with geometric functionality including camera calibration, 
disparity, range and normal map estimation, and geometric image transformations."""

from .hitnet import create_hitnet_matcher

from .image_transformations import (
    PixelMap,
    compute_pixel_map,
    invert_pixel_map,
    remap_image_pixels,
)

from .point_cloud import (
    PointCloud,
    PointCloudLoader,
    PointCloudProcessor,
)

from .point_cloud_processors import (
    downsample_point_cloud,
    estimate_point_cloud_normals,
    create_downsampler,
    create_normal_estimator,
)

from .range_maps import (
    compute_range_from_disparity,
    compute_points_from_range,
    compute_normals_from_range,
)

from .stereo_geometry import (
    StereoGeometry,
    compute_stereo_geometry,
    distort_stereo_geometry,
)

from .stereo_matcher import StereoMatcher

from .stereo_rectification import (
    StereoRectificationTransforms,
    StereoRectificationResult,
    compute_rectifying_camera_transforms,
    compute_rectifying_image_transforms,
    compute_stereo_rectification,
    rectify_image_pair,
)


__all__ = [
    "create_hitnet_matcher",
    # ...
    "PixelMap",
    "compute_pixel_map",
    "invert_pixel_map",
    "remap_image_pixels",
    # ...
    "PointCloud",
    "PointCloudLoader",
    "PointCloudProcessor",
    # ...
    "downsample_point_cloud",
    "estimate_point_cloud_normals",
    "create_downsampler",
    "create_normal_estimator",
    # ...
    "compute_range_from_disparity",
    "compute_points_from_range",
    "compute_normals_from_range",
    # ...
    "StereoGeometry",
    "compute_stereo_geometry",
    "distort_stereo_geometry",
    # ...
    "StereoMatcher",
    # ...
    "StereoRectificationTransforms",
    "StereoRectificationResult",
    "compute_rectifying_camera_transforms",
    "compute_rectifying_image_transforms",
    "compute_stereo_rectification",
    "rectify_image_pair",
]
