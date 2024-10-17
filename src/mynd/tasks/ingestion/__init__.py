"""Package for project setup tasks."""

from .config_types import CameraGroupConfig, ProjectConfig
from .executor import execute_project_setup
from .metadata import map_metadata_to_cameras

__all__ = [
    "CameraGroupConfig",
    "ProjectConfig",
    "execute_project_setup",
    "map_metadata_to_cameras",
]
