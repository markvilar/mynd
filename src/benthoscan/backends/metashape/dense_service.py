"""Module that implements the dense service for the Metashape backend."""

from collections.abc import Callable
from pathlib import Path

import Metashape

from result import Ok, Err, Result

from ...registration import PointCloudLoader, create_point_cloud_loader

from .context import _backend_data

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
        key: create_point_cloud_loader(source=path)
        for key, path in point_cloud_files.items()
    }

    return point_cloud_loaders


def request_dense_models(
    output_dir: Path,
    overwrite: bool,
) -> Result[dict[int, PointCloudLoader], str]:
    """Export point clouds from a document to a cache dirctory."""

    document: Metashape.Document = _backend_data.get("document", None)

    if document is None:
        return Err("no document loaded")

    loaders: dict[int, PointCloudLoader] = export_dense_cloud_and_configure_loaders(
        document=document,
        output_dir=output_dir,
        overwrite=overwrite,
    )

    return Ok(loaders)


"""
Dense processors:
 - build_depth_maps
 - build_point_cloud
 - build_mesh
 - build_coordinate_map
 - build_texture
"""


def build_dense_processor(config: dict) -> Result[Callable, str]:
    """TODO"""

    processor: str = config["process"]
    enabled: bool = config["enabled"]
    parameters: dict = config["parameters"]

    match processor:
        case "build_depth_maps":
            return Ok(partial(build_depth_maps, parameters=parameters))
        case "build_point_cloud":
            return Ok(partial(build_point_cloud, parameters=parameters))
        case "build_texture":
            return Ok(partial(build_texture, parameters=parameters))
        case _:
            return Err(f"invalid processor: {processor}")


def build_depth_maps(
    chunk: Metashape.Chunk,
    progress_fun: ProgressCallback,
    parameters: dict,
) -> Result[None, str]:
    """Builds depth maps for the given chunk."""
    with stdout_redirected():
        try:
            chunk.buildDepthMaps(
                **parameters,
                filter_mode=Metashape.MildFiltering,
                progress=progress_fun,
            )
        except BaseException as error:
            return Err(error)

    return Ok(None)


def build_point_cloud(
    chunk: Metashape.Chunk,
    progress_fun: ProgressCallback,
    parameters: dict,
) -> Result[None, str]:
    """Builds a dense point cloud for the given chunk."""
    with stdout_redirected():
        try:
            chunk.buildPointCloud(
                **parameters,
                progress=progress_fun,
            )
        except BaseException as error:
            return Err(error)

    return Ok(None)


def build_mesh(
    chunk: Metashape.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback,
) -> Result[None, str]:
    """Builds a mesh model for the given chunk."""
    # TODO: Add mapping for Metashape internal argument types
    with stdout_redirected():
        try:
            chunk.buildModel(
                source_data=Metashape.DepthMapsData,
                surface_type=Metashape.Arbitrary,
                interpolation=Metashape.EnabledInterpolation,
                progress=progress_fun,
            )
        except BaseException as error:
            return Err(error)

    return Ok(None)


def build_coordinate_map(
    chunk: Metashape.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback = None,
) -> Result[None, str]:
    """Builds a coordinate map for the given chunk."""

    # TODO: Add conversion support for the following type: Metashape.GenericMapping,

    with stdout_redirected():
        try:
            chunk.buildUV(
                **parameters,
                progress=progress_fun,
            )
        except BaseException as error:
            return Err(error)

    return Ok(None)


def build_texture(
    chunk: Metashape.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback = None,
) -> Result[None, str]:
    """Builds a model texture for the given chunk."""

    # TODO: Look for option to only use left cameras.
    # TODO: Add conversion support for the following type: Metashape.MosaicBlending,

    with stdout_redirected():
        try:
            chunk.buildTexture(
                **parameters,
                progress=progress_fun,
            )
        except BaseException as error:
            return Err(error)

    return Ok(None)


DENSE_PROCESSORS = {
    "build_depth_maps": build_depth_maps,
    "build_point_cloud": build_point_cloud,
    "build_mesh": build_mesh,
    "build_coordinate_map": build_coordinate_map,
    "build_texture": build_texture,
}
