"""Module for setting up project data, i.e. chunks with image files, 
camera groups, and camera references."""

from pathlib import Path
from typing import Callable

import polars as pl

from loguru import logger
from result import Ok, Err, Result

from benthoscan.cameras import Camera, MonocularCamera, StereoCamera
from benthoscan.containers import Registry, create_file_registry_from_directory
from benthoscan.project import Document, load_document, create_document
from benthoscan.spatial import SpatialReference, build_references_from_dataframe
from benthoscan.io import read_toml

from .config_types import (
    ChunkSetupData,
    ProjectSetupData,
    ChunkSetupConfig,
    ProjectSetupConfig,
)


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
    camera_type: str = camera_config["camera_type"]

    match camera_type:
        case "monocular":
            return create_mono_cameras_from_dataframe(
                camera_data,
                camera_config["label"],
            )
        case "stereo":
            return create_stereo_cameras_from_dataframe(
                camera_data,
                camera_config["labels"]["master"],
                camera_config["labels"]["slave"],
            )
        case _:
            return Err(f"invalid camera type: {camera_type}")


def register_images_from_directory(
    directory: Path, labeller: Callable[[Path], str]
) -> Registry[str, Path]:
    """Lists image files from a directory, labels them, and adds them to
    a registry."""

    registry: Registry[str, Path] = create_file_registry_from_directory(
        directory,
        extensions=[".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    # TODO: Move image file extensions to config?
    image_files: list[Path] = find_files_with_extension(
        directory=directory,
        extensions=[".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    registry: Registry[str, Path] = Registry[str, Path]()

    for path in image_files:
        label: str = labeller(path)
        registry.insert(label, path)

    return registry


def prepare_chunk_setup_data(config: ChunkSetupConfig) -> ChunkSetupData:
    """Prepares a chunk for initialization by registering images, and
    loading cameras and references."""

    camera_data: pl.DataFrame = pl.read_csv(config.camera_file)
    camera_config: dict = read_toml(config.camera_config).unwrap()

    # Create cameras from a dataframe under the assumption that we only have one group,
    # i.e. one setup (mono, stereo, etc.) for all the cameras
    cameras: list[Camera] = create_cameras_from_dataframe(
        camera_data, camera_config["camera"]
    ).unwrap()

    references: list[SpatialReference] = build_references_from_dataframe(
        camera_data,
        camera_config["reference"]["column_maps"],
        camera_config["reference"]["constants"],
    ).unwrap()

    reference_registry: Registry[str, SpatialReference] = Registry[
        str, SpatialReference
    ]()
    for reference in references:
        reference_registry.insert(reference.identifier.label, reference)

    # TODO: Move file extensions to config
    image_registry: Registry[str, Path] = create_file_registry_from_directory(
        directory,
        extensions=[".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    return ChunkSetupData(
        config.chunk_name,
        cameras=cameras,
        image_registry=image_registry,
        reference_registry=reference_registry,
    )


def prepare_project_setup_data(config: ProjectSetupConfig) -> ProjectSetupData:
    """Creates project setup data based on the given project configuration."""

    chunks: list[ChunkSetupData] = [
        prepare_chunk_setup_data(chunk) for chunk in config.chunks
    ]

    if config.document.create_new:
        document: Document = create_document(config.document.path).unwrap()
    else:
        document: Document = load_document(config.document.path).unwrap()

    logger.info(document)

    return ProjectSetupData(document, chunks)
