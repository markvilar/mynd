"""Module for writing Metashape objects to JSON files."""
from typing import Dict, Callable, List, TypeAlias

import Metashape

from loguru import logger

# JSON primitive data types
JsonTypes: TypeAlias = float | int | str | bool | Dict | List 

JsonObject: TypeAlias = Dict[str, JsonTypes]

# Map with JSON converts for Metashape objects
METASHAPE_JSON_FUNS: Dict[type, Callable[[], Dict]]= {
    Metashape.Camera: None,
    Metashape.CameraGroup: None,
    Metashape.Camera.Reference: None,
    Metashape.CameraTrack: None,
    Metashape.ChunkTransform: None,
    Metashape.CirTransform: None,
    Metashape.CoordinateSystem: None,
    
    Metashape.DepthMaps: None,
    
    Metashape.Elevation: None,
    Metashape.EulerAngles: None,

    Metashape.Marker: None,
    Metashape.MarkerGroup: None,
    Metashape.Mask: None,
    Metashape.Matrix: None,
    Metashape.MetaData: None,
    Metashape.Model: None,

    Metashape.Orthomosaic: None,
   
    Metashape.Photo: None,
    Metashape.PointCloud: None,
   
    Metashape.RasterTransform: None,
    Metashape.Region: None,

    Metashape.Scalebar: None,
    Metashape.Sensor: None,
    Metashape.Shapes: None,

    Metashape.Thumbnails: None,
    Metashape.TiePoints: None,
    Metashape.TiledModel: None,

    Metashape.Vector: None,
}

def convert_camera_to_json(camera: Metashape.Camera) -> JsonObject:
    """Converts a Metashape camera to a JSON object."""
    return {
        # "calibration": camera.calibration, # TODO
        "center": camera.center, # TODO
        "chunk": camera.chunk.label,
        "enabled": camera.enabled,
        "frames": len(camera.frames), # type: List of Camera
        "group": camera.group, # type: CameraGroup
        "key": camera.key,
        "label": camera.label,
        "master": camera.master.label,
        # "meta": camera.meta,
        "photo": str(camera.photo.path),
        "planes": len(camera.planes), # type: List of Camera
        "reference": convert_camera_reference_to_json(camera.reference), # type: Camera.Reference
        "selected": camera.selected,
        "sensor": camera.sensor.key, # type: Sensor
        "shutter": camera.shutter, # type: Shutter
        # "thumbnail": camera.thumbnail, # type: Thumbnail
        "transform": convert_matrix_to_json(camera.transform), # type: Matrix
        "type": str(camera.type),
    }

def convert_vector_to_json(vector: Metashape.Vector) -> JsonObject:
    """Converts a Metashape vector to a JSON object."""
    if vector is None:
        return None
    return list((vector.x, vector.y, vector.z, vector.w))

def convert_calibration_to_json(calibration: Metashape.Calibration) -> JsonObject:
    """Converts a Metashape calibration to a JSON object."""
    # TODO: Implement
    raise NotImplementedError

def convert_camera_reference_to_json(reference: Metashape.Camera.Reference) -> JsonObject:
    """Converts a Metashape camera reference to a JSON object."""
    data = {
        "accuracy": convert_vector_to_json(reference.accuracy),
        "enabled": reference.enabled,
        "location": convert_vector_to_json(reference.location),
        "location_accuracy": convert_vector_to_json(reference.location_accuracy),
        "location_enabled": reference.location_enabled,
        "rotation": convert_vector_to_json(reference.rotation),
        "rotation_accuracy": convert_vector_to_json(reference.rotation_accuracy),
        "rotation_enabled": reference.rotation_enabled,
    }
    return data

def convert_matrix_to_json(matrix: Metashape.Matrix) -> JsonObject:
    """Converts a Metashape matrix to a JSON object."""
    if matrix is None:
        return None

    return list(matrix)
