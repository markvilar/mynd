"""Module for point cloud IO, i.e. reading and writing point clouds."""

from pathlib import Path
from typing import Callable

import Metashape
import open3d

from result import Ok, Err, Result


PointCloud = open3d.data.PLYPointCloud
ProgressCallback = Callable[[float], None]


PointCloudLoader = Callable[[None], Result[PointCloud, str]]


def write_point_cloud(
    chunk: Metashape.Chunk,
    path: str | Path,
    progress_fun: ProgressCallback = lambda percent: None,
) -> Result[Path, str]:
    """Exports a point cloud from a Metashape chunk to a file."""

    try:
        chunk.exportPointCloud(
            path=str(path),  # Path to output file.
            source_data=Metashape.DataSource.PointCloudData,
            binary=True,
            save_point_normal=True,
            save_point_color=True,
            save_point_classification=False,
            save_point_confidence=False,
            save_comment=False,
            progress=progress_fun,
        )
    except BaseException as error:
        return Err(str(error))

    return Ok(Path(path))


def read_point_cloud(path: str | Path) -> Result[PointCloud, str]:
    """Loads a point cloud from a file."""

    try:
        point_cloud: PointCloud = open3d.io.read_point_cloud(str(path))
        return Ok(point_cloud)
    except IOError as error:
        return Err(str(error))
