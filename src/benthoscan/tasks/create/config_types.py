"""Module for project setup task configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat

from result import Ok, Err, Result

from benthoscan.cameras import Camera
from benthoscan.containers import Registry
from benthoscan.project import Document
from benthoscan.spatial import SpatialReference


@dataclass
class ChunkSetupConfig:
    """Class representing a chunk configuration."""

    chunk_name: str
    image_directory: Path
    camera_file: Path
    camera_config: Path


@dataclass
class DocumentSetupConfig:
    """Class representing a document configuration."""

    path: Path
    create_new: bool


@dataclass
class ProjectSetupConfig:
    """Class representing a project configuration."""

    document: DocumentSetupConfig
    chunks: list[ChunkSetupConfig] = field(default_factory=list)

    def __repr__(self) -> str:
        """Returns a printable representation of the object."""
        string: str = f"ProjectSetupConfig: \n{pformat(self.document)} \n{pformat(self.chunks)}"
        return string


@dataclass
class ChunkSetupData:
    """Class representing chunk setup data."""

    chunk_name: str
    cameras: list[Camera]
    image_registry: Registry[str, Path]
    reference_registry: Registry[str, SpatialReference]


@dataclass
class ProjectSetupData:
    """Class representing project setup data."""
    
    document: Document
    chunks: list[ChunkSetupData]
