"""Module for stereo cameras."""

import Metashape as ms

from mynd.collections import GroupID, StereoCameraGroup
from mynd.utils.result import Ok, Result

from .. import helpers as helpers
from .common import retrieve_chunk_and_dispatch


def retrieve_stereo_cameras(
    identifier: GroupID,
) -> Result[StereoCameraGroup, str]:
    """Retrieve stereo cameras from the target group. If an error with a
    message if no document is loaded."""
    return retrieve_chunk_and_dispatch(
        identifier, retrieve_stereo_cameras_callback
    )


def retrieve_stereo_cameras_callback(
    chunk: ms.Chunk,
    identifier: GroupID,
) -> Result[StereoCameraGroup, str]:
    """Callback that retrieves stereo cameras from a Metashape chunk."""
    stereo_cameras: list[StereoCameraGroup] = helpers.get_stereo_group(chunk)
    return Ok(stereo_cameras)
