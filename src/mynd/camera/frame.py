"""Module for camera frames."""

from typing import NamedTuple, Optional, Self

from .sensor import Sensor


#@dataclass(eq=True, frozen=True)
class Frame(NamedTuple):
    """Class representing a frame with multiple components."""

    ImageKey = str

    key: int
    components: dict[Sensor, ImageKey]

#    def __init__(self: Self, key: int, components: dict[Sensor, ImageKey]) -> None:
#        """Initialization method."""
#        object.__setattr__(self, "key", key)
#        object.__setattr__(self, "components", components)

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
