"""Library with geometric functionality including camera calibration, disparity, range and normal 
estimation, and geometric image transformations."""

from .hitnet import (
    HitnetConfig,
    load_hitnet,
    compute_disparity,
)

from .image_transformations import (
    PixelMap,
    compute_pixel_map,
    invert_pixel_map,
    remap_image_pixels,
)

from .point_cloud import PointCloud


from .range_maps import (
    compute_range_from_disparity,
    compute_points_from_range,
    compute_normals_from_range,
)

from .rectification import (
    RectificationTransforms,
    RectificationResult,
    compute_rectifying_camera_transforms,
    compute_rectifying_image_transforms,
    compute_stereo_rectification,
    rectify_image_pair,
)


__all__ = [
    "HitnetConfig",
    "load_hitnet",
    "compute_disparity",
    "PixelMap",
    "compute_pixel_map",
    "invert_pixel_map",
    "remap_image_pixels",
    "get_image_corners",
    "PointCloud",
    "PointCloudLoader",
    "read_point_cloud",
    "create_point_cloud_loader",
    "compute_range_from_disparity",
    "compute_points_from_range",
    "compute_normals_from_range",
    "CameraCalibration",
    "RectificationTransforms",
    "RectificationResult",
    "compute_rectifying_camera_transforms",
    "compute_rectifying_image_transforms",
    "compute_stereo_rectification",
    "rectify_image_pair",
]
