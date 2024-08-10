""" Functionality to create summaries for various Metashape objects. """

from typing import Callable, List

import Metashape

from ...utils.log import logger


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
    attributes: List[str],
    func: Callable[str, None],
) -> None:
    """TODO:"""
    for attribute in attributes:
        value = getattr(instance, attribute)
        string = f"{attribute}: {value}"
        func(string)
