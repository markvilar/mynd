"""TODO"""

import Metashape

from loguru import logger

from benthoscan.cameras import Camera, StereoCamera
from benthoscan.spatial import SpatialReference
from benthoscan.project import (
    Document,
    Chunk,
    save_document,
    create_chunk,
    add_camera_group,
    add_camera_references,
)

from .config_types import ProjectSetupData


def setup_project_data(project: ProjectSetupData) -> None:
    """TODO"""

    document: Document = project.document

    for data in project.chunks:
        chunk: Result[Chunk, str] = create_chunk(document, data.chunk_name)

        # TODO: Move chunk and camera CRS to config
        chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
        chunk.camera_crs = Metashape.CoordinateSystem("EPSG::4326")

        # Add camera group to configure images and sensors
        result: Result[None, str] = add_camera_group(
            chunk, data.cameras, data.image_registry, logger.info
        )

        if result.is_err():
            logger.error(result.err())

        result: Result[None, str] = add_camera_references(
            chunk,
            data.cameras,
            data.reference_registry,
        )

        if result.is_err():
            logger.error(result.err())

    save_result: Result[Path, str] = save_document(document)
    if save_result.is_err():
        logger.error(f"{save_result.err()}")
    else:
        logger.info(f"saved document to: {save_result.ok()}")
