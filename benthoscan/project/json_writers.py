"""Module for writing Metashape objects to JSON files."""
from typing import Dict, List, TypeAlias

import Metashape

# JSON primitive data types
JSON_TYPES: TypeAlias = float | int | str | bool | Dict | List 


def convert_chunk_to_json(chunk: Metashape.Chunk) -> None:
    """Convert a Metashape chunk to a JSON dictionary."""
    json = dict()

    json = {
        "label": chunk.label,
        "cameras": len(chunk.cameras),
        "sensors": len(chunk.sensors),
        "camera_crs": str(chunk.camera_crs),
        "camera_groups": len(chunk.camera_groups),
        "camera_location_accuracy": str(chunk.camera_location_accuracy),
        "camera_rotation_accuracy": str(chunk.camera_rotation_accuracy),
        "camera_track": len(chunk.camera_track),
        "camera_tracks": len(chunk.camera_tracks),
        "cir_transform": str(chunk.cir_transform),
        "elevation": chunk.elevation,
        "elevations": chunk.elevations,
        "enabled": chunk.enabled,
        "euler_angles": str(chunk.euler_angles),
        "marker_crs": str(chunk.marker_crs),
        "marker_groups": len(chunk.marker_groups),
        "markers": len(chunk.markers),
        "meta",
        "model",
        "models",
        "modified",
        "raster_transform",
        "region",
        "shapes",
        "tie_points",
        "tiepoint_accuracy",
        "tiled_model",
        "transform",
        "world_crs",
    }
    pass
