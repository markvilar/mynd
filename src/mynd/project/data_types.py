"""Module for data types related to projects."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from ..data.camera import Sensor, Frame
from ..containers import Registry
from ..spatial import SpatialReference


ImageKey = str


@dataclass(frozen=True)
class CameraGroupData:
    """Class representing a group of camera data, including cameras, images, and references."""

    name: str
    sensors: set[Sensor]
    frames: list[Frame]  # mapping from sensor to image key
    images: Registry[ImageKey, Path]  # mapping from image key to file
    references: Registry[str, SpatialReference]  # mapping from image key to reference

    def __init__(
        self: Self,
        name: str,
        sensors: set[Sensor],
        frames: list[Frame],
        images: Registry[ImageKey, Path],
        references: Registry[str, SpatialReference],
    ) -> Self:
        """Initializes the object."""
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "sensors", sensors)
        object.__setattr__(self, "frames", frames)
        object.__setattr__(self, "images", images)
        object.__setattr__(self, "references", references)

    def __post_init__(self: Self) -> Self:
        """Validates the camera group data."""
        # TODO: Make sure that only one sensor is master
        # TODO: Validate that all frames have the same collection of sensors
        # TODO: Validate that the sensors coincide with the frame sensors
        pass

    def __repr__(self: Self) -> str:
        """Returns a string representation of the object."""

        sensor_count: int = len(self.sensors)
        frame_count: int = len(self.frames)
        image_count: int = len(self.images)
        reference_count: int = len(self.references)

        attributes: str = (
            f"name={self.name}, sensors={sensor_count}, frames={frame_count}, "
            + f"images={image_count}, references={reference_count}"
        )

        return f"CameraGroupData({attributes})"

    def get_sensor_images(self: Self) -> dict[Sensor, ImageKey]:
        """Returns the image keys for each image captured by a sensor."""
        collections: dict[Sensor, ImageKey] = {
            sensor: list() for sensor in self.sensors
        }

        for frame in self.frames:
            for sensor, image_key in frame.components.items():
                collections[sensor].append(image_key)

        return collections


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
