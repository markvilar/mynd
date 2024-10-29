"""Module for camera sensors."""

from dataclasses import dataclass
from typing import Self, TypeAlias

from .calibration import CameraCalibration


@dataclass
class Sensor:
    """Class representing a sensor."""

    @dataclass(frozen=True)
    class Identifier:
        """Class representing a sensor identifier."""

        key: int
        label: str = ""


    @dataclass(frozen=True)
    class Reference:
        """Class representing a sensor reference."""

        fixed_location: bool = False
        fixed_rotation: bool = False
        location: list | None = None
        rotation: list | None = None
        location_accuracy: list | None = None
        rotation_accuracy: list | None = None

    identifier: Identifier

    width: int
    height: int

    calibration: CameraCalibration | None = None
    master: Identifier | None = None
    reference: Reference | None = None
    bands: list[dict] | None = None

    def __post_init__(self: Self) -> Self:
        """Post initialization method."""
        self.sort_index = self.identifier.key
        return self

    def __hash__(self: Self) -> Self:
        """Hash dunder method."""
        return self.key

    @property
    def size(self: Self) -> tuple[int, int]:
        """Returns the size, i.e. the width and height, of the sensor."""
        return self.width, self.height

    def has_calibration(self: Self) -> bool:
        """Returns true if the sensor has a calibration."""
        return self.calibration is not None

    def has_master(self: Self) -> bool:
        """Returns true if the sensor has a master."""
        return self.master is not None

    def has_reference(self: Self) -> bool:
        """Returns true if the sensor has a reference."""
        return self.reference is not None

    def has_bands(self: Self) -> bool:
        """Returns true if the sensor has assigned bands."""
        return self.bands is not None


SensorID: TypeAlias = Sensor.Identifier
