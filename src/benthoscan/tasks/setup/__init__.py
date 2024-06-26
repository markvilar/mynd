"""Package for project setup tasks."""

from .config_types import (
    ProjectSetupConfig,
    DocumentSetupConfig,
    ChunkSetupConfig,
    ProjectSetupData,
    ChunkSetupData,
)

from .executor import execute_project_setup
