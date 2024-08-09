"""Interface class for cameras."""

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Optional, Self


class CameraType(StrEnum):
    MONOCULAR = auto()
    STEREO = auto()
    UNKNOWN = auto()


CameraLabel = str


@dataclass(eq=True, frozen=True)
class Sensor:
    """Class representing a frame sensor."""

    key: int
    label: str

    master: bool
    width: int
    height: int

    fixed_location: bool = False
    fixed_rotation: bool = False

    location: Optional[list] = None
    rotation: Optional[list] = None
    location_accuracy: Optional[list] = None
    rotation_accuracy: Optional[list] = None

    bands: Optional[list[dict]] = None

    def __init__(
        self: Self,
        key: int,
        label: str,
        master: bool,
        width: int,
        height: int,
        fixed_location: bool = False,
        fixed_rotation: bool = False,
        location: Optional[list] = None,
        rotation: Optional[list] = None,
        location_accuracy: Optional[list] = None,
        rotation_accuracy: Optional[list] = None,
        bands: Optional[list[dict]] = None,
    ) -> Self:
        """Initialization method."""

        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "master", master)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "fixed_location", fixed_location)
        object.__setattr__(self, "fixed_rotation", fixed_rotation)

        object.__setattr__(self, "location", location)
        object.__setattr__(self, "rotation", rotation)
        object.__setattr__(self, "location_accuracy", location_accuracy)
        object.__setattr__(self, "rotation_accuracy", rotation_accuracy)
        object.__setattr__(self, "bands", bands)

    def __post_init__(self: Self) -> Self:
        """Post initialization method."""
        self.sort_index = self.key
        return self

    def __hash__(self: Self) -> Self:
        """Hash dunder method."""
        return self.key

    @property
    def size(self: Self) -> tuple[int, int]:
        """Returns the size, i.e. the width and height, of the sensor."""
        return self.width, self.height

    @property
    def has_bands(self: Self) -> bool:
        """Returns true if the sensor has assigned bands."""
        return not self.bands is None

    @property
    def has_location(self: Self) -> bool:
        """Returns true if the sensor has a location."""
        return not self.location is None

    @property
    def has_rotation(self: Self) -> bool:
        """Returns true if the sensor has a rotation."""
        return not self.rotation is None

    @property
    def has_location_accuracy(self: Self) -> bool:
        """Returns true if the sensor has a location accuracy."""
        return not self.location_accuracy is None

    @property
    def has_rotation_accuracy(self: Self) -> bool:
        """Returns true if the sensor has a rotation accuracy."""
        return not self.rotation_accuracy is None


@dataclass(eq=True, frozen=True)
class Frame:
    """Class representing a frame with multiple components."""

    ImageKey = str

    key: int
    components: dict[Sensor, ImageKey]

    def __init__(self: Self, key: int, components: dict[Sensor, ImageKey]) -> None:
        """Initialization method."""
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "components", components)

    def __post_init__(self: Self) -> Self:
        """Post initialization method."""
        # TODO: Validate that atleast one of the sensors is master
        is_master: list[bool] = [sensor.master for sensor in self.components]
        assert sum(is_master) == 1, "frame can only have one master sensor"
        self.sort_index = self.key

    def __hash__(self: Self) -> Self:
        """Hash dunder method."""
        return self.key

    def __len__(self: Self) -> int:
        """Returns the number of components in the frame."""
        return len(self.components)

    @property
    def master_sensor(self: Self) -> Optional[Sensor]:
        """Returns the master sensor for the frame."""
        master = None
        for sensor in self.sensors:
            if sensor.master:
                master = sensor

        return master

    @property
    def sensors(self: Self) -> list[Sensor]:
        """Returns the sensors in the frame."""
        return list(self.components.keys())

    @property
    def image_keys(self: Self) -> list[ImageKey]:
        """Returns the image keys in the frame."""
        return list(self.components.values())

    def get(self: Self, sensor: Sensor, default=None) -> Optional[Sensor]:
        """Gets an image key from the frame."""
        return self.components.get(sensor, default)
