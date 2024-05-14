"""Module for handling chunk data, i.e. image files, camera groups, and camera references."""

from dataclasses import dataclass

from loguru import logger

from benthoscan.project import Chunk

from .config import ChunkConfig

@dataclass
class ChunkData():

    image_loader: object
    camera_loader: object
    reference_loader: object


def prepare_chunk(chunk: Chunk, config: ChunkConfig) -> Chunk:
    """Prepares a chunk for initialization by registering images, and
    loading cameras and references."""

    logger.info(chunk)
    logger.info(config)

    # TODO: Create image loader

    # TODO: Create camera loader

    # TODO: Create reference loader

    # TODO: Load camera settings
    # TODO: Load reference settings

    raise NotImplementedError("prepare_chunk is not implemented")
