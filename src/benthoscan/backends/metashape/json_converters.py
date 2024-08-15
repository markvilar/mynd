"""Module for writing Metashape objects to JSON files."""

from collections.abc import Callable
from typing import TypeAlias

import Metashape

from ...utils.log import logger

# JSON primitive data types
JsonTypes: TypeAlias = float | int | str | bool | dict | list

JsonObject: TypeAlias = dict[str, JsonTypes]


# Map with JSON converts for Metashape objects
METASHAPE_JSON_FUNS: dict[type, Callable[[object], dict]] = {
    Metashape.Camera: None,
    Metashape.CameraGroup: None,
    Metashape.Camera.Reference: None,
    Metashape.CameraTrack: None,
    Metashape.Chunk: None,
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


"""
Metashape to JSON conversion functions:
 - convert_chunk_to_json
 - convert_camera_to_json
 - convert_vector_to_json
 - convert_calibration_to_json
 - convert_camera_reference_to_json
 - convert_matrix_to_json
"""


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
    }

    """
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
    """

    raise NotImplementedError("convert_chunk_to_json is not implemented")


def convert_camera_to_json(camera: Metashape.Camera) -> JsonObject:
    """Converts a Metashape camera to a JSON object."""
    return {
        # "calibration": camera.calibration, # TODO
        "center": camera.center,  # TODO
        "chunk": camera.chunk.label,
        "enabled": camera.enabled,
        "frames": len(camera.frames),  # type: list of Camera
        "group": camera.group,  # type: CameraGroup
        "key": camera.key,
        "label": camera.label,
        "master": camera.master.label,
        # "meta": camera.meta,
        "photo": str(camera.photo.path),
        "planes": len(camera.planes),  # type: list of Camera
        "reference": convert_camera_reference_to_json(
            camera.reference
        ),  # type: Camera.Reference
        "selected": camera.selected,
        "sensor": camera.sensor.key,  # type: Sensor
        "shutter": camera.shutter,  # type: Shutter
        # "thumbnail": camera.thumbnail, # type: Thumbnail
        "transform": convert_matrix_to_json(camera.transform),  # type: Matrix
        "type": str(camera.type),
    }


def convert_vector_to_json(vector: Metashape.Vector) -> JsonObject:
    """Converts a Metashape vector to a JSON object."""
    return list((vector.x, vector.y, vector.z, vector.w))


def convert_calibration_to_json(calibration: Metashape.Calibration) -> JsonObject:
    """Converts a Metashape calibration to a JSON object."""
    # TODO: Implement
    raise NotImplementedError


def convert_camera_reference_to_json(
    reference: Metashape.Camera.Reference,
) -> JsonObject:
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
    return list(matrix)


"""
Summary functions:
 - summarize_chunk
 - summarize_sensor
 - summarize_camera
 - summarize_object_instance
"""


def summarize_chunk(chunk: Metashape.Chunk, func: Callable[str, None] = None) -> None:
    """Summarizes a Metashape chunk."""
    attributes = [
        "camera_crs",
        "camera_groups",
        "camera_location_accuracy",
        "camera_rotation_accuracy",
        "camera_track",
        "camera_tracks",
        "cameras",
        "cir_transform",
        "elevation",
        "elevations",
        "enabled",
        "euler_angles",
        "label",
        "marker_crs",
        "marker_groups",
        "markers",
        "meta",
        "model",
        "models",
        "modified",
        "raster_transform",
        "region",
        "sensors",
        "shapes",
        "tie_points",
        "tiepoint_accuracy",
        "tiled_model",
        "transform",
        "world_crs",
    ]

    summarize_object_instance(chunk, attributes, func)


def summarize_sensor(
    sensor: Metashape.Sensor,
    func: Callable[str, None] = None,
) -> None:
    """Summarize a Metashape sensor."""
    attributes = [
        "antenna",
        "bands",
        "black_level",
        "calibration",
        "chunk",
        "data_type",
        "fixed",
        "fixed_calibration",
        "fixed_location",
        "fixed_params",
        "fixed_rotation",
        "focal_length",
        "height",
        "width",
        "rotation",
        "location",
    ]
    summarize_object_instance(sensor, attributes, func)


def summarize_camera(
    camera: Metashape.Camera,
    func: Callable[str, None] = None,
) -> None:
    """Summarizes a Metashape camera."""
    attributes = [
        "chunk",
        "key",
        "label",
        "master",
        "photo",
        "planes",
        "reference",
        "rotation_covariance",
        "selected",
        "sensor",
        "type",
    ]
    summarize_object_instance(camera, attributes, func)


def summarize_object_instance(
    instance: object,
    attributes: list[str],
    func: Callable[str, None],
) -> None:
    """Summarizes a python object by extracting attribute-value pairs from them."""
    for attribute in attributes:
        value = getattr(instance, attribute)
        string = f"{attribute}: {value}"
        func(string)
