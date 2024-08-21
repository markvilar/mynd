"""Package that implements the backend for Metashape."""

from .camera_helpers import (
    get_sensor_pairs,
    get_camera_pairs,
    get_stereo_groups,
    render_range_and_normal_maps,
    compute_camera_matrix,
    compute_distortion_vector,
    compute_camera_calibration,
    compute_stereo_extrinsics,
    compute_stereo_calibration,
)

from .data_types import (
    SensorPair,
    CameraPair,
    StereoGroup,
)

from .image import (
    image_to_numpy,
    load_image_pair,
)
    
from .context import (
    log_internal_data,
    load_project,
    save_project,
)

from .dense_service import request_dense_models
from .ingest_service import request_data_ingestion
from .sparse_service import request_sparse_processor_info

__all__ = [
    "SensorPair",
    "CameraPair",
    "StereoGroup",
    "get_sensor_pairs",
    "get_camera_pairs",
    "get_stereo_groups",
    "image_to_array",
    "render_range_and_normal_maps",
    "compute_camera_matrix",
    "compute_distortion_vector",
    "compute_camera_calibration",
    "compute_stereo_extrinsics",
    "compute_stereo_calibration",

    "log_internal_data",
    "load_project",
    "save_project",

    "request_dense_models",
    "request_data_ingestion",
    "request_sparse_processor_info",
]
