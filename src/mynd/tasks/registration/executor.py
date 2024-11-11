"""Module for executing registration tasks."""

from pathlib import Path

from mynd.geometry import PointCloud, PointCloudLoader
from mynd.io import read_point_cloud
from mynd.utils.result import Err, Result


def execute_point_cloud_registration() -> Result[None, str]:
    """Executes a point cloud registration task."""

    DATA_DIR: Path = Path("/home/martin/dev/mynd/.cache")

    point_cloud_files: dict[int, Path] = {
        0: DATA_DIR / Path("qdc5ghs3_20100430_024508.ply"),
        1: DATA_DIR / Path("qdc5ghs3_20120501_033336.ply"),
        2: DATA_DIR / Path("qdc5ghs3_20130405_103429.ply"),
        3: DATA_DIR / Path("qdc5ghs3_20210315_230947.ply"),
    }

    def create_point_cloud_loader(path: Path) -> PointCloudLoader:
        """Creates a point cloud loader."""

        def loader() -> Result[PointCloud, str]:
            """Loads a point cloud."""
            return read_point_cloud(path)

        return loader

    loaders: dict[int, PointCloudLoader] = {
        key: create_point_cloud_loader(path)
        for key, path in point_cloud_files.items()
        if path.exists()
    }

    count: int = len(loaders)
    if count < 2:
        return Err(f"invalid number of point clouds for registration: {count}")

    # TODO: Set up registration schema
    # TODO: Build registration processes
    # TODO: Run registration processes

    return Err("execute_point_cloud_registration is not implemented")
