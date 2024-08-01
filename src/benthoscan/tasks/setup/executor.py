"""Module for executing project setup tasks."""

import polars as pl

from result import Ok, Err, Result

from ...cameras import create_cameras_from_dataframe
from ...containers import Registry, create_file_registry_from_directory
from ...io import read_toml
from ...spatial import SpatialReference, build_references_from_dataframe
from ...utils.log import logger
from ...project import DocumentOptions, CameraGroupData, ProjectData


from .config_types import CameraGroupConfig, ProjectConfig


def configure_project_options(config: ProjectConfig) -> ProjectData:
    """TODO"""

    chunks: list[CameraGroupData] = [
        configure_camera_groups(chunk) for chunk in config.chunks
    ]


    if config.document.create_new:
        document: Document = create_document()
        result: Result[Path, str] = save_document(document, config.document.path)
        if result.is_err():
            logger.error(f"failed to create document: {config.document.path}")
    else:
        document: Document = load_document(config.document.path).unwrap()

    return ProjectData(document, chunks)


def configure_camera_groups(config: CameraGroupConfig) -> CameraGroupData:
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
        config.image_directory,
        extensions=[".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    return CameraGroupData(
        config.name,
        cameras=cameras,
        image_registry=image_registry,
        reference_registry=reference_registry,
    )


def execute_project_setup(config: ProjectConfig) -> Result[ProjectData, str]:
    """TODO"""

    document: DocumentOptions = config.document_options
    groups: list[CameraGroupConfig] = config.camera_groups

    m: Path = config.document_options.path
    n: bool = config.document_options.create_new

    camera_groups: list[CameraGroupData] = [
        configure_camera_groups(chunk) for chunk in config.camera_groups
    ]
    
    project_data: ProjectData = ProjectData(
        document_options = config.document_options,
        camera_groups = camera_groups,
    )
        
    return Ok(project_data)
