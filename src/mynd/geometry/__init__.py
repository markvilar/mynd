"""Package with geometric functionality including camera calibration, 
disparity, range and normal map estimation, and geometric image transformations."""

from .hitnet import create_hitnet_matcher

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

from .stereo_geometry import (
    StereoGeometry,
    compute_stereo_geometry,
    distort_stereo_geometry,
    create_stereo_geometry_tiles,
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
    "StereoGeometry",
    "compute_stereo_geometry",
    "distort_stereo_geometry",
    "create_stereo_geometry_tiles",
    "StereoMatcher",
    "StereoRectificationTransforms",
    "StereoRectificationResult",
    "compute_rectifying_camera_transforms",
    "compute_rectifying_image_transforms",
    "compute_stereo_rectification",
    "rectify_image_pair",
]
