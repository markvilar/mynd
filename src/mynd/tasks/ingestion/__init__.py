"""Package for project setup tasks."""

from .config_types import CameraGroupConfig, ProjectConfig
from .executor import execute_project_setup

__all__ = [
    "CameraGroupConfig",
    "ProjectConfig",
    "execute_project_setup",
]
