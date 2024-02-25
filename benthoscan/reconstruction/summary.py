""" Functionality to create summaries for various Metashape objects. """
from typing import Callable

import Metashape

from loguru import logger

def summarize_chunk(chunk: Metashape, func: Callable[str, None]=None) -> None:
    """ Summarizes a Metashape chunk. """
    entries = [
        f"Chunk:          {chunk}",
        f"Cameras:        {len(chunk.cameras)}",
        f"Sensors:        {len(chunk.sensors)}",
        f"CRS:            {chunk.camera_crs}",
        f"Camera roups:   {chunk.camera_groups}",
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

    if not func: return 

    for entry in entries:
        func(entry)

def summarize_sensor(
    sensor: Metashape.Sensor, 
    func: Callable[str, None]=None,
) -> None:
    """ Summarize a Metashape sensor. """
    attributes = [attr for attr in dir(sensor) if not attr.startswith('__')]
    if not func: return 
    for entry in attributes:
        func(entry)
