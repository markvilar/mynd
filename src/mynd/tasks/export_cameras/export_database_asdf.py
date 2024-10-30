"""Module for exporting cameras to ASDF files."""

from pathlib import Path

from mynd.collections import CameraGroup
from mynd.io.asdf import treeify_camera_group, write_tree

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err


def export_camera_database_asdf(
    destination: Path,
    cameras: CameraGroup,
) -> None:
    """Exports cameras to an ASDF database."""

    tree: dict = treeify_camera_group(cameras)

    match write_tree(destination, tree, all_array_compression="zlib"):
        case Ok(None):
            logger.info("successfully wrote camera group")
        case Err(error):
            logger.error(error)
