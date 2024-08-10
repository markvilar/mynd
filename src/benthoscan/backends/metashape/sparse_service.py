"""Module for sparse and dense reconstruction processors."""

from collections.abc import Callable
from functools import partial

import Metashape

from result import Ok, Err, Result

from ...utils.log import logger
from ...utils.redirect import stdout_redirected


"""
Sparse processors:
 - match images
 - align cameras
 - optimize cameras
"""


MATCH_PARAMETERS = {
    "quality": int,  # NOTE: 0: "highest", 1: "high", 2: "medium", 3: "low", 4: "lowest"
    "generic_preselection": bool,  #
    "reference_preselection": bool,
    "keypoint_limit": int,
    "tiepoint_limit": int,
    "pairs": list[tuple[int, int]],
    "cameras": list[int],
    "reset_matches": bool,
}


MATCH_RESULTS = {
    "image_matches": dict,
}


ALIGN_PARAMETERS = {
    "cameras": list[int],
    "point_clouds": list[int],
    "min_image": int,
    "adaptive_fitting": bool,
    "reset_alignment": bool,
    "subdivide_task": bool,
}


ALIGN_RESULTS = {
    "camera_poses": list,
    "sensor_calibrations": list,
    "tie_points": list,
}


OPTIMIZE_PARAMETERS = {
    "fit_f": bool,
    "fit_cx": bool,  # Enable optimization of X principal point coordinates.
    "fit_cy": bool,  # Enable optimization of Y principal point coordinates.
    "fit_b1": bool,  # Enable optimization of aspect ratio.
    "fit_b2": bool,  # Enable optimization of skew coefficient.
    "fit_k1": bool,  # Enable optimization of k1 radial distortion coefficient.
    "fit_k2": bool,  # Enable optimization of k2 radial distortion coefficient.
    "fit_k3": bool,  # Enable optimization of k3 radial distortion coefficient.
    "fit_k4": bool,  # Enable optimization of k3 radial distortion coefficient.
    "fit_p1": bool,  # Enable optimization of p1 tangential distortion coefficient.
    "fit_p2": bool,  # Enable optimization of p2 tangential distortion coefficient.
    "fit_corrections": bool,  # Enable optimization of additional corrections.
    "adaptive_fitting": bool,  # Enable adaptive fitting of distortion coefficients.
    "tiepoint_covariance": bool,  # Estimate tie point covariance matrices.
}


OPTIMIZE_RESULTS = {
    "camera_pose_covariances": list,
    "tie_point_covariances": list,
}


SPARSE_PROCESSOR_PARAMETERS: dict[str, dict] = {
    "match_images": MATCH_PARAMETERS,
    "align_cameras": ALIGN_PARAMETERS,
    "optimize_cameras": OPTIMIZE_PARAMETERS,
}


SPARSE_PROCESSOR_RESULTS: dict[str, dict] = {
    "match_images": MATCH_RESULTS,
    "align_cameras": ALIGN_RESULTS,
    "optimize_cameras": OPTIMIZE_RESULTS,
}


ProgressCallback = Callable[[float], None]


def match_images(
    chunk: Metashape.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback,
) -> Result[None, str]:
    """Matches the images in the chunk."""

    # TODO: Map reference preselection mode to Metashapes options
    with stdout_redirected():
        try:
            chunk.matchPhotos(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)

    return Ok(None)


def align_cameras(
    chunk: Metashape.Chunk, progress_fun: ProgressCallback, parameters: dict
) -> Result[None, str]:
    """Aligns the cameras in the chunk."""
    with stdout_redirected():
        try:
            chunk.alignCameras(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)

    return Ok(None)


def optimize_cameras(
    chunk: Metashape.Chunk, progress_fun: ProgressCallback, parameters: dict
) -> Result[None, str]:
    """Optimizes the calibration and camera poses in the chunk."""
    with stdout_redirected():
        try:
            chunk.optimizeCameras(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)

    return Ok(None)


def build_sparse_processor(config: dict) -> Result[Callable, str]:
    """TODO"""

    processor_type: str = config["process"]
    enabled: bool = config["enabled"]
    parameters: dict = config["parameters"]

    match processor_type:
        case "match_images":
            return Ok(partial(match_images, parameters=parameters))
        case "align_cameras":
            return Ok(partial(align_cameras, parameters=parameters))
        case "optimize_cameras":
            return Ok(partial(optimize_cameras, parameters=parameters))
        case _:
            return Err(f"invalid processor type: {processor_type}")


def request_sparse_processor_info() -> dict[str, dict]:
    """Returns the sparse processors for the backend."""

    return SPARSE_PROCESSOR_PARAMETERS
