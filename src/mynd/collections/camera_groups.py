"""Module for camera API types."""

from dataclasses import dataclass, field
from typing import Optional

from ..camera import Camera, CameraCalibration, Sensor
from ..image import ImageLoader
from ..containers import Pair


CameraID = Camera.Identifier
SensorID = Sensor.Identifier


@dataclass
class CameraGroup:
    """Class representing a facade for camera groups."""

    @dataclass(frozen=True)
    class Identifier:
        """Class representing a camera group Identifier."""

        key: int
        label: str

    @dataclass
    class Attributes:
        """Class representing a group of camera attributes."""

        identifiers: list[CameraID] = field(default_factory=list)
        image_labels: dict[CameraID, str] = field(default_factory=dict)
        masters: dict[CameraID, CameraID] = field(default_factory=dict)
        sensors: dict[CameraID, SensorID] = field(default_factory=dict)

    @dataclass
    class References:
        """Class representing references for a camera group."""

        identifiers: list[CameraID] = field(default_factory=list)
        locations: dict[CameraID, list] = field(default_factory=dict)
        rotations: dict[CameraID, list] = field(default_factory=dict)

    identifier: Optional[Identifier] = None
    attributes: Optional[Attributes] = None
    estimated_references: Optional[References] = None
    prior_references: Optional[References] = None


@dataclass
class StereoCameraGroup:
    """Class representing a stereo camera group."""

    # TODO: Add sensors
    # TODO: Add camera keys
    calibrations: Pair[CameraCalibration]
    image_loaders: list[Pair[ImageLoader]]
