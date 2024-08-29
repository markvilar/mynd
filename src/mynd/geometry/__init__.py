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

from .range_maps import (
    compute_range_from_disparity,
    compute_points_from_range,
    compute_normals_from_range,
)

from .stereo import (
    CameraCalibration,
    StereoExtrinsics,
    StereoCalibration,
    StereoHomography,
    RectificationResult,
    compute_rectifying_homographies,
    compute_rectifying_pixel_maps,
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
    # TODO: Test function "get_image_corners",

    "compute_range_from_disparity",
    "compute_points_from_range",
    "compute_normals_from_range",

    "CameraCalibration",
    "StereoExtrinsics",
    "StereoCalibration",
    "StereoHomography",
    "RectificationResult",
    "compute_rectifying_homographies",
    "compute_rectifying_pixel_maps",
    "compute_stereo_rectification",
    "rectify_image_pair",
]
