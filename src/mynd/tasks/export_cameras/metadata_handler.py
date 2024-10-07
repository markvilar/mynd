"""Module to handle export of camera metadata."""

from collections.abc import Mapping

from ...camera import Camera
from ...io.h5 import H5Database
from ...utils.result import Result


CameraID = Camera.Identifier


def handle_metadata_export(
    storage: H5Database.Group, metadata: Mapping[CameraID, dict]
) -> Result[None, str]:
    """Handles exporting of camera metadata."""

    # TODO: Figure out how to write metadata to H5 files

    raise NotImplementedError("handle_metadata_export is not implemented")
