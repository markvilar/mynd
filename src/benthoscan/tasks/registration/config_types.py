"""Module for registration task configuration types."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RegistrationTaskConfig:
    """Class representing a registration task configuration."""

    point_cloud_files: dict[str, Path]
