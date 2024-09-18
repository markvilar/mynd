"""Package with API data types."""

from .camera import CameraIndexGroup, CameraReferenceGroup, StereoGroup
from .identifier import GroupID

__all__ = [
    "CameraIndexGroup",
    "CameraReferenceGroup",
    "StereoGroup",
    "GroupID",
]
