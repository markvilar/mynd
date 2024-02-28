""" Functions for """
from collections import OrderedDict
from pathlib import Path
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
    grouped_images: List[OrderedDict[str, Path]],
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

    # TODO: Inject image group order, i.e. to allow the user to specify the
    # ordering of groups. Change OrderedDict to Dict if the order is injected.
    
    # Merge item-based groups into 
    files, group_sizes = list(), list()
    for images in grouped_images:
        image_paths: List[Path] = list(images.values())
        image_paths: List[str] = [str(path) for path in image_paths]
        files.extend(image_paths)
        group_sizes.append(len(image_paths))

    # Validate
    all([size == group_sizes[0] for size in group_sizes])

    # Add images to chunk
    chunk.addPhotos(
        filenames=files, 
        filegroups=group_sizes, 
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


    """
    importReference(path='', format=ReferenceFormatCSV, columns='', delimiter='', 
        group_delimiters=False, skip_rows=0 [ , items ][ , crs ] , 
        ignore_labels=False, create_markers=False,
        threshold=0.1, shutter_lag=0 [ , progress ] 
    )

    Import reference data from the specified file.
    Parameters
    path (string) – Path to the file with reference data.
    format (ReferenceFormat) – File format.
    columns (string) – Column order in csv format (
        n - label, 
        o - enabled flag, 
        x/y/z - coordinates, 
        X/Y/Z - coordinate accuracy, 
        a/b/c - rotation angles, 
        A/B/C - rotation angle accuracy,
        [] - group of multiple values, 
        | - column separator within group
    ).
    delimiter (string) – Column delimiter in csv format.
    group_delimiters (bool) – Combine consecutive delimiters in csv format.
    skip_rows (int) – Number of rows to skip in (csv format only).
    items (ReferenceItems) – List of items to load reference for (csv format only).
    crs (CoordinateSystem) – Reference data coordinate system (csv format only).
    ignore_labels (bool) – Matches reference data based on coordinates alone (csv format only).
    create_markers (bool) – Create markers for missing entries (csv format only).
    threshold (float) – Error threshold in meters used when ignore_labels is set (csv format only).
    shutter_lag (float) – Shutter lag in seconds (APM format only).
    """
