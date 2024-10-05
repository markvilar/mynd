"""Package for Metashape camera services."""

from .camera import (
    get_camera_attributes,
    get_estimated_camera_references,
    get_prior_camera_references,
)

from .stereo import (
    get_stereo_cameras,
)

from .metadata import (
    update_camera_metadata,
    get_camera_metadata,
)

__all__ = [
    "get_camera_attributes",
    "get_estimated_camera_references",
    "get_prior_camera_references",
    "get_stereo_cameras",
    "update_camera_metadata",
    "get_camera_metadata",
]
