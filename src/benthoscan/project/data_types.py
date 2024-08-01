"""Module for data types related to projects."""

from dataclasses import dataclass, field
from pathlib import Path

from ..cameras import Camera
from ..containers import Registry
from ..spatial import SpatialReference


@dataclass
class CameraGroupData:
    """Class representing a group of camera data, including cameras, images, and references."""

    name: str
    cameras: list[Camera]
    image_registry: Registry[str, Path]
    reference_registry: Registry[str, SpatialReference]

    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        
        camera_count: int = len(self.cameras)
        image_count: int = len(self.image_registry)
        reference_count: int = len(self.reference_registry)
        
        attributes: str = f"name={self.name}, cameras={camera_count}, " \
            + f"images={image_count}, references={reference_count}"
        string: str = f"CameraGroupData({attributes})"
        return string


@dataclass
class DocumentOptions:
    """Class representing options for document initialization and loading."""

    path: Path
    create_new: bool


@dataclass
class ProjectData:
    """Class representing project setup data."""

    document_options: DocumentOptions
    camera_groups: list[CameraGroupData] = field(default_factory=list)
