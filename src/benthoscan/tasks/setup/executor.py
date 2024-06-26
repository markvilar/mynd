"""Module for executing project setup tasks."""

import Metashape

from loguru import logger
from result import Ok, Err, Result

from benthoscan.cameras import add_camera_group, add_camera_references
from benthoscan.project import create_chunk

from .config_types import ProjectSetupData


def execute_project_setup(project: ProjectSetupData) -> Result[None, str]:
    """TODO"""

    document: Metashape.Document = project.document

    for data in project.chunks:
        chunk: Result[Metashape.Chunk, str] = create_chunk(document, data.chunk_name)

        # TODO: Move chunk and camera CRS to config
        chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
        chunk.camera_crs = Metashape.CoordinateSystem("EPSG::4326")

        # Add camera group to configure images and sensors
        result: Result[None, str] = add_camera_group(
            chunk, data.cameras, data.image_registry, logger.info
        )

        if result.is_err():
            logger.error(result.err())
            return result

        result: Result[None, str] = add_camera_references(
            chunk,
            data.cameras,
            data.reference_registry,
        )

        if result.is_err():
            logger.error(result.err())
            return result

    return Ok(None)
