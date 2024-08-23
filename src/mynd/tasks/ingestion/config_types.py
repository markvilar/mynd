"""Module for project setup task configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat


from ...project import DocumentOptions


@dataclass
class CameraGroupConfig:
    """Class representing a chunk configuration."""

    name: str
    image_directory: Path
    camera_data: Path
    camera_config: Path


@dataclass
class ProjectConfig:
    """Class representing a project configuration."""

    document_options: DocumentOptions
    camera_groups: list[CameraGroupConfig] = field(default_factory=list)

    def __repr__(self) -> str:
        """Returns a printable representation of the object."""
        string: str = (
            f"IngestionConfig: \n - {pformat(self.document_options)} \n - {pformat(self.camera_groups)}"
        )
        return string
