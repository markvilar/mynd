"""Module for managing export of camera attributes, metadata, and images."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypeVar, TypeAlias

from mynd.collections import CameraGroup, SensorImages
from mynd.image import (
    ImageType,
)


from mynd.utils.filesystem import Resource
from mynd.utils.log import logger
from mynd.utils.result import Result

# Import handlers for subtasks
from .export_database_h5 import export_camera_database_h5
from .export_data_frame import export_camera_data_frame


Resources: TypeAlias = list[Resource]
ImageResourceGroups: TypeAlias = Mapping[ImageType, Resources]


T: TypeVar = TypeVar("T")


ErrorType = str
ResultType = Result[T, ErrorType]


@dataclass
class ExportData:
    """Class representing export data."""

    cameras: CameraGroup
    image_groups: Optional[list[SensorImages]] = None

    def has_images(self) -> bool:
        """Returns true if the export data contains images."""
        return self.image_groups is not None


def export_camera_group(
    destination: Path,
    cameras: CameraGroup,
) -> ResultType[None]:
    """Entrypoint for exporting camera groups. Prepares export data,
    and dispatches to the relevant subtasks.

    :arg destination:   export destination path
    :arg cameras:       group of camera data (attributes, references)
    :arg images:        image resource groups
    """

    # TODO: Export stereo rectification in camera database
    log_task_header(cameras)

    match destination.suffix:
        case ".h5" | ".hdf5":
            export_camera_database_h5(
                destination, cameras, error_callback=logger.error
            )
        case ".asdf":
            raise NotImplementedError
        case ".csv":
            export_camera_data_frame(destination, cameras)
        case _:
            raise NotImplementedError


def log_task_header(cameras: CameraGroup) -> None:
    """Logs a header with summary statistics before exporting cameras."""

    group_label: str = cameras.group_identifier.label
    camera_count: int = len(cameras.attributes.identifiers)
    estimated_count: int = len(cameras.reference_estimates.identifiers)
    prior_count: int = len(cameras.reference_priors.identifiers)

    logger.info("")
    logger.info(f"Exporting camera group: {group_label}")
    logger.info(f"Camera attributes:      {camera_count}")
    logger.info(f"Estimated references:   {estimated_count}")
    logger.info(f"Prior references:       {prior_count}")
    logger.info("")


def on_error(message: str) -> None:
    """Callback that is called on an error result."""
    logger.error(message)
