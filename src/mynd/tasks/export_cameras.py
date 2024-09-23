"""Module for exporting camera data including keys, labels, images, and references."""

from dataclasses import dataclass
from pathlib import Path

from ..api import CameraBundle, Identifier
from ..utils.result import Result


@dataclass
class ExportCameraConfig:
    """Class representing an export camera configuration."""

    destination: str | Path


def export_camera_data(
    identifier: Identifier, bundle: CameraBundle
) -> Result[str, str]:
    """Exports camera data to a given destination."""

    pass
