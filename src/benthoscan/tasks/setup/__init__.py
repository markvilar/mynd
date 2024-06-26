"""Package for project setup tasks."""

from .config_types import (
    ProjectSetupConfig,
    DocumentSetupConfig,
    ChunkSetupConfig,
    ProjectSetupData,
    ChunkSetupData,
)

from .worker import execute_project_setup
