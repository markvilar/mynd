""" Functions for """
from pathlib import Path
from typing import Dict, List

import Metashape

Camera = Metashape.Camera
Chunk = Metashape.Chunk
Sensor = Metashape.Sensor

def add_camera_to_chunk(chunk: Chunk, sensor: Sensor) -> Camera:
    """ Adds a camera to a chunk. """
    return chunk.addCamera(sensor)

def add_image_groups_to_chunk(
    chunk: Chunk, 
    image_groups: List[Dict[str, Path]]
) -> None:
    """ Adds images to a chunk. """
    return chunk.addPhotos(
        filenames=images, 
        filegroups=groups, 
        layout=Metashape.MultiplaneLayout,
    )

def add_images_to_chunk(chunk: Chunk, image_paths: List[Path]) -> None:
    """ Adds images to a chunk. """
    return chunk.addPhotos(
        filenames=images, 
        filegroups=groups, 
        layout=Metashape.MultiplaneLayout,
    )
    
    """
    addPhotos([filenames ][, filegroups ], layout=UndefinedLayout[, group ], strip_extensions=True,
    load_reference=True, load_xmp_calibration=True, load_xmp_orientation=True,
    load_xmp_accuracy=False, load_xmp_antenna=True, load_rpc_txt=False[, progress ])
    Add a list of photos to the chunk.
    Parameters
    • filenames (list of string) – List of files to add.
    • filegroups (list of int) – List of file groups.
    • layout (ImageLayout) – Image layout.
    • group (int) – Camera group key.
    • strip_extensions (bool) – Strip file extensions from camera labels.
    • load_reference (bool) – Load reference coordinates.
    • load_xmp_calibration (bool) – Load calibration from XMP meta data.
    • load_xmp_orientation (bool) – Load orientation from XMP meta data.
    • load_xmp_accuracy (bool) – Load accuracy from XMP meta data.
    • load_xmp_antenna (bool) – Load GPS/INS offset from XMP meta data.
    • load_rpc_txt (bool) – Load satellite RPC data from auxiliary TXT files.
    • progress (Callable[[float], None]) – Progress callback.
    """
