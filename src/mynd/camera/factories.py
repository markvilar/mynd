"""Module for building cameras from various sources."""

from typing import NamedTuple

import polars as pl

from ..utils.result import Ok, Err, Result

from .frame import Frame
from .sensor import Sensor


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


@static_vars(counter=0)
def create_sensor(config: dict) -> Sensor:
    """Creates a sensor from the given configuration."""
    key = create_sensor.counter
    create_sensor.counter += 1
    return Sensor(key=key, **config)


@static_vars(counter=0)
def create_frame(components: dict[Sensor, str]) -> Frame:
    """Creates a frame with the given configuration."""
    key = create_frame.counter
    create_frame.counter += 1
    return Frame(key=key, components=components)


class FrameMap(NamedTuple):
    """Class representing a mapping from sensor to column."""

    sensor: str
    column: str


def read_frames_from_dataframe(
    dataframe: pl.DataFrame,
    mappings: list[dict],
    sensors: list[Sensor],
) -> Result[list[Frame], str]:
    """Reads frames from a data frame by mapping image labels to sensors
    for each row."""

    # Create a lookup for sensors and frames for convenience
    sensor_maps: dict = {sensor.label: sensor for sensor in sensors}
    frame_maps: list[FrameMap] = [FrameMap(**item) for item in mappings]

    # Validate mapping against sensors
    for mapping in frame_maps:
        if mapping.sensor not in sensor_maps:
            return Err(f"sensor label not in sensors: {mapping.sensor}")

    # Validate mapping against the data frame
    for mapping in frame_maps:
        if mapping.column not in dataframe.columns:
            return Err(f"frame column not in data frame: {mapping.column}")

    # For every captured frame, i.e. row in the dataframe, we create a mapping from sensor
    # to column
    frames: list[Frame] = list()
    for row in dataframe.iter_rows(named=True):
        columns: dict[str, str] = {
            mapping.sensor: row[mapping.column] for mapping in frame_maps
        }
        components: dict[Sensor, str] = {
            sensor_maps[key]: value for key, value in columns.items()
        }

        frame: Frame = create_frame(components)
        frames.append(frame)

    return Ok(frames)
