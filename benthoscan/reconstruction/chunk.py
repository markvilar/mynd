""" Functions for """
from dataclasses import dataclass
from typing import Dict, List

import Metashape

from loguru import logger

Camera = Metashape.Camera
Chunk = Metashape.Chunk
Document = Metashape.Document
Sensor = Metashape.Sensor

def create_chunk(document: Document, label: str=None) -> Chunk:
    """ Creates a chunk for the given document. """
    chunk = document.addChunk()
    if label:
        chunk.label = label
    return chunk

def add_camera_to_chunk(chunk: Chunk, sensor: Sensor) -> Camera:
    """ Adds a camera to a chunk. """
    return chunk.addCamera(sensor)

def add_image_groups_to_chunk(
    chunk: Chunk, 
    file_groups: Dict[str, Dict[int, str]],
    file_keys: List[str],
) -> None:
    """ 
    Adds groups of images to a chunk. The images are formatted in item-based
    order, meaning that each item has images from several sources.
    The function assumes that all items have the same set of sources.

    Example grouping:
        [ 
            { "left" : "left_01.png", "right" : "right_01.png" },
            { "left" : "left_02.png", "right" : "right_02.png" },
            ...
        ]
    """
    filenames = list()
    filegroups = list()
    for items in file_groups:
        for key in file_keys:
            filenames.append(str(items[key]))
        filegroups.append(len(items))
    
    # Validate
    all([size == filegroups[0] for size in filegroups])

    # Add images to chunk
    chunk.addPhotos(
        filenames = filenames, 
        filegroups = filegroups, 
        layout = Metashape.MultiplaneLayout,
        progress = None
    )
