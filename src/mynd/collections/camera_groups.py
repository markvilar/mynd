"""Module for camera API types."""

from dataclasses import dataclass, field
from typing import Self, TypeAlias

from mynd.camera import (
    Camera,
    CameraID,
    CameraCalibration,
    SensorID,
    Sensor,
    StereoRig,
)
from mynd.image import ImageLoader
from mynd.utils.containers import Pair


@dataclass(frozen=True)
class GroupIdentifier:
    """Class representing a group identifier."""

    key: int
    label: str


GroupID: TypeAlias = GroupIdentifier


@dataclass
class CameraGroup:
    """Class representing a facade for camera groups."""

    @dataclass
    class Attributes:
        """Class representing a group of camera attributes."""

        identifiers: list[CameraID] = field(default_factory=list)
        image_labels: dict[CameraID, str] = field(default_factory=dict)
        masters: dict[CameraID, CameraID] = field(default_factory=dict)
        camera_sensors: dict[CameraID, SensorID] = field(default_factory=dict)
        sensors: list[Sensor] = field(default_factory=list)

        @property
        def sensor_cameras(self: Self) -> dict[SensorID, list[CameraID]]:
            """Returns the cameras for each sensors."""
            cameras: dict[SensorID, list[CameraID]] = dict()
            for camera, sensor in self.camera_sensors.items():
                if sensor not in cameras:
                    cameras[sensor] = list()

                cameras[sensor].append(camera)

            return cameras

        @property
        def stereo_rigs(self: Self) -> list[StereoRig]:
            """Returns master-slave pairs of sensors."""
            stereo_rigs: list[StereoRig] = list()
            sensor_map: dict[SensorID, Sensor] = {
                sensor.identifier: sensor for sensor in self.sensors
            }

            for sensor in self.sensors:
                if not sensor.has_master():
                    continue

                master: Sensor = sensor_map.get(sensor.master)
                slave: Sensor = sensor
                stereo_rigs.append(StereoRig(Pair(master, slave)))

            return stereo_rigs

    @dataclass
    class References:
        """Class representing references for a camera group."""

        identifiers: list[CameraID] = field(default_factory=list)
        locations: dict[CameraID, list] = field(default_factory=dict)
        rotations: dict[CameraID, list] = field(default_factory=dict)

    @dataclass
    class Metadata:
        """Class representing metadata for a camera group."""

        fields: dict[CameraID, Camera.Metadata] = field(default_factory=dict)

    group_identifier: GroupID | None = None
    attributes: Attributes | None = None
    reference_estimates: References | None = None
    reference_priors: References | None = None
    metadata: Metadata | None = None


@dataclass
class StereoCameraGroup:
    """Class representing a stereo camera group."""

    # TODO: Add sensors
    group_identifier: GroupID
    calibrations: Pair[CameraCalibration]
    camera_pairs: list[Pair[CameraID]]
    image_loaders: dict[CameraID, ImageLoader]
