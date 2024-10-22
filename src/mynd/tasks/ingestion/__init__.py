"""Package for project setup tasks."""

from .cameras import execute_project_setup
from .metadata import map_metadata_to_cameras, ingest_metadata_locally

__all__ = [
    "execute_project_setup",
    "map_metadata_to_cameras",
    "ingest_metadata_locally",
]
