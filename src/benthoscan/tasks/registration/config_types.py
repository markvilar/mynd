"""Module for registration task configuration types."""

from dataclasses import dataclass
from pathlib import Path

from benthoscan.spatial import PointCloudLoader


@dataclass
class RegistrationTaskConfig:
    """Class representing a registration task configuration."""

    point_cloud_loaders: dict[int, PointCloudLoader]
