"""Module for building cameras from various sources."""

import polars as pl

from result import Ok, Err, Result

from .camera_types import CameraType, Camera, MonocularCamera, StereoCamera


def create_mono_cameras_from_dataframe(
    camera_data: pl.DataFrame, label: str
) -> Result[list[MonocularCamera], str]:
    """TODO"""

    if not label in camera_data.columns:
        return Err(f"camera label is not in data frame: {label}")

    cameras: list[MonocularCamera] = list()
    for row in camera_data.iter_rows(named=True):
        cameras.append(MonocularCamera(row[label]))

    return Ok(cameras)


def create_stereo_cameras_from_dataframe(
    camera_data: pl.DataFrame, master: str, slave: str
) -> Result[list[StereoCamera], str]:
    """TODO"""

    if not master in camera_data.columns:
        return Err(f"camera label not in data frame: {master}")

    if not slave in camera_data.columns:
        return Err(f"camera label not in data frame: {slave}")

    cameras: list[StereoCamera] = list()
    for row in camera_data.iter_rows(named=True):
        cameras.append(StereoCamera(row[master], row[slave]))

    return Ok(cameras)


def create_cameras_from_dataframe(
    camera_data: pl.DataFrame, camera_config: dict
) -> Result[list[Camera], str]:
    """TODO"""

    if not "group_name" in camera_config:
        return Err(f"missing camera config key: 'group_name'")
    if not "camera_type" in camera_config:
        return Err(f"missing camera config key: 'camera_type'")

    group_name: str = camera_config["group_name"]

    camera_type: CameraType = CameraType(camera_config["camera_type"])

    match camera_type:
        case CameraType.MONOCULAR:
            return create_mono_cameras_from_dataframe(
                camera_data,
                camera_config["label"],
            )
        case CameraType.STEREO:
            return create_stereo_cameras_from_dataframe(
                camera_data,
                camera_config["labels"]["master"],
                camera_config["labels"]["slave"],
            )
        case _:
            return Err(f"invalid camera type: {camera_type}")
