""" Functionality to create summaries for various Metashape objects. """

from typing import Callable, List

import Metashape

from loguru import logger


def summarize_chunk(chunk: Metashape, func: Callable[str, None] = None) -> None:
    """Summarizes a Metashape chunk."""
    entries = [
        f"Chunk:          {chunk}",
        f"Cameras:        {len(chunk.cameras)}",
        f"Sensors:        {len(chunk.sensors)}",
        f"CRS:            {chunk.camera_crs}",
        f"Camera groups:  {chunk.camera_groups}",
        f"Pos. accuracy:  {chunk.camera_location_accuracy}",
        f"Rot. accuracy:  {chunk.camera_rotation_accuracy}",
        f"Track:          {chunk.camera_track}",
        f"Tracks:         {chunk.camera_tracks}",
        f"CIR Transform:  {chunk.cir_transform}",
        f"Elevation:      {chunk.elevation}",
        f"Elevations:     {chunk.elevations}",
        f"Enabled:        {chunk.enabled}",
        f"Euler angles:   {chunk.euler_angles}",
    ]

    if not func:
        return

    for entry in entries:
        func(entry)


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
