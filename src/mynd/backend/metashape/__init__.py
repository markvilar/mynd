"""Package that implements the Mynd backend with Metashape."""

from .context import (
    log_internal_data,
    load_project,
    get_project_url,
    get_group_identifiers,
    save_project,
)

from .camera_services import (
    get_camera_attributes,
    get_estimated_camera_references,
    get_prior_camera_references,
    get_stereo_cameras,
)

from .dense_services import request_dense_models
from .sparse_services import request_sparse_processor_info

# TODO: Update to new ingestion task
# from .ingestion_services import request_data_ingestion


__all__ = [
    "log_internal_data",
    "load_project",
    "get_project_url",
    "get_group_identifiers",
    "save_project",
    "get_camera_attributes",
    "get_estimated_camera_references",
    "get_prior_camera_references",
    "get_stereo_cameras",
    "request_dense_models",
    # "request_data_ingestion", # TODO: Update the new ingestion task
    "request_sparse_processor_info",
]
