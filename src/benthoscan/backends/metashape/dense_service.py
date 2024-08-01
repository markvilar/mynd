"""Module that implements the dense service for the Metashape backend."""

import functools

from collections.abc import Callable
from pathlib import Path

import Metashape

from result import Ok, Err, Result

from ...runtime import Command, load_environment
from ...registration import PointCloudLoader, read_point_cloud

from .project import load_document, save_document

ProgressCallback = Callable[[float], None]


def export_dense_cloud(
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


def export_dense_cloud_and_configure_loaders(
    document: Metashape.Document,
    output_dir: Path,
    overwrite: bool,
) -> dict[int, PointCloudLoader]:
    """Exports dense clouds and returns loaders for each of them."""

    point_cloud_files: dict[int, Path] = dict()
    for chunk in document.chunks:
        if not chunk.enabled:
            continue

        output_path: Path = output_dir / f"{chunk.label}.ply"

        if output_path.exists() and not overwrite:
            file_path: Path = output_path
        else:
            file_path: Path = export_dense_cloud(chunk, path=output_path).unwrap()

        point_cloud_files[chunk.key] = file_path

    point_cloud_loaders: dict[int, PointCloudLoader] = {
        key: functools.partial(read_point_cloud, path=path)
        for key, path in point_cloud_files.items()
    }

    return point_cloud_loaders


def request_dense_models(
    document_path: Path,
    cache_directory: Path,
    overwrite: bool,
) -> Result[dict[int, PointCloudLoader], str]:
    """Export point clouds from a document to a cache dirctory."""

    load_result: Result[Metashape.Document, str] = load_document(document_path)

    match load_result:
        case Ok(document):
            loaders: dict[int, PointCloudLoader] = (
                export_dense_cloud_and_configure_loaders(
                    document = document,
                    output_dir = cache_directory,
                    overwrite = overwrite,
                )
            )
            return Ok(loaders)
        case Err(error):
            return Err(error)
        case _:
            raise NotImplementedError("invalid result case")
