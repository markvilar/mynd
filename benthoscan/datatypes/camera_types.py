"""Interface class for cameras."""

from dataclasses import dataclass, field
from typing import Callable, List, Optional, TypeAlias

from benthoscan.datatypes.geometry import Vec3


@dataclass
class Camera:
    """Data class representing a camera with a key, an image key, and an
    optional camera reference with position and orientation."""

    @dataclass
    class Labels:
        """Data class for camera labels."""

        camera: str
        image: str

    @dataclass
    class Reference:
        """Data class for a camera reference."""

        position: Optional[Vec3] = None
        orientation: Optional[Vec3] = None
        position_accuracy: Optional[Vec3] = None
        orientation_accuracy: Optional[Vec3] = None

    # Type aliases
    Reference = Reference

    labels: Labels
    group: Optional[str] = None
    reference: Optional[Reference] = None

    def __hash__(self) -> str:
        """Returns a hash for the camera."""
        return hash((self.labels.camera, self.labels.image))

    @property
    def has_group(self) -> bool:
        """Returns true if the camera is part of a group."""
        return not self.group is None

    @property
    def has_reference(self) -> bool:
        """Returns true if the camera has a reference."""
        return not self.reference is None


# Camera type aliases
Cameras: TypeAlias = List[Camera]
CameraFactory: TypeAlias = Callable[[None], Cameras]


@dataclass(frozen=True)
class CameraAssembly:
    """Data class for an assembly of cameras. The assembly has one master
    camera and a variable number of slave cameras."""

    master: Camera
    slaves: List[Camera] = field(default_factory=list)

    def __init__(
        self,
        master: Camera,
        slaves: List[Camera] = None,
    ) -> None:
        """Initialization method."""
        object.__setattr__(self, "master", master)
        object.__setattr__(self, "slaves", slaves)

    @property
    def cameras(self) -> Cameras:
        """Returns the cameras in the assembly as a list. The master camera is
        always the first camera in the list."""
        items = list([self.master])
        items.extend(self.slaves)
        return items

    @property
    def count(self) -> int:
        """Returns the number of cameras in the assembly."""
        return len(self.cameras)

    def has_slaves(self) -> bool:
        """Returns true if the assembly has slaves."""
        return not self.slaves is None


# Camera assembly type aliases
CameraAssemblies: TypeAlias = List[CameraAssembly]
CameraAssemblyFactory: TypeAlias = Callable[[None], CameraAssemblies]
