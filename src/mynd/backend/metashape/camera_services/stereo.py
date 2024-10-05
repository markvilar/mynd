"""Module for stereo cameras."""

import Metashape as ms

from mynd.collections import CameraGroup, StereoCameraGroup
from mynd.utils.result import Ok, Result

from .camera_helpers import get_stereo_group
from .common import retrieve_chunk_and_dispatch


GroupID = CameraGroup.Identifier


def get_stereo_cameras(identifier: GroupID) -> Result[StereoCameraGroup, str]:
    """Gets stereo cameras from the target group. If an error with a
    message if no document is loaded."""
    return retrieve_chunk_and_dispatch(identifier, stereo_camera_callback)


def stereo_camera_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[StereoCameraGroup, str]:
    """Callback that retrieves stereo cameras from a document"""
    stereo_cameras: list[StereoCameraGroup] = get_stereo_group(chunk)
    return Ok(stereo_cameras)
