"""Entrypoint for invoking project setup / initialization tasks from the command-line interface."""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

import polars as pl

from result import Ok, Err, Result

from benthoscan.cameras import create_cameras_from_dataframe
from benthoscan.containers import Registry, create_file_registry_from_directory
from benthoscan.io import read_toml
from benthoscan.project import Document, load_document, create_document, save_document
from benthoscan.runtime import Command
from benthoscan.spatial import SpatialReference, build_references_from_dataframe
from benthoscan.utils.log import logger

from benthoscan.tasks.setup import ChunkSetupConfig, DocumentSetupConfig, ProjectSetupConfig
from benthoscan.tasks.setup import ChunkSetupData, ProjectSetupData
from benthoscan.tasks.setup import execute_project_setup


def parse_project_setup_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """Creates an argument parser and parses the given arguments."""
    parser = ArgumentParser()

    # Document arguments
    parser.add_argument("document", type=Path, help="document path")
    parser.add_argument("data_directory", type=Path, help="data directory")
    parser.add_argument(
        "--new", action=BooleanOptionalAction, help="create new document"
    )

    # Chunk / data arguments
    parser.add_argument(
        "chunk_config", type=Path, default=None, help="data configuration file"
    )

    namespace = parser.parse_args(arguments)

    if not namespace:
        return Err(f"failed to parse arguments: {arguments}")

    return Ok(namespace)


def create_project_setup_config(
    document: Path, create_new: bool, data_directory: Path, chunk_config: Path
) -> Result[ProjectSetupConfig, str]:
    """Creates a project configuration consisting of document and chunk configurations."""

    document_config: DocumentSetupConfig = DocumentSetupConfig(document, create_new)

    read_result: Result[dict, str] = read_toml(chunk_config)
    if read_result.is_err():
        return read_result

    config: dict = read_result.ok()

    chunk_configs: list[ChunkSetupConfig] = list()
    for chunk in config["chunk"]:
        chunk_config: ChunkSetupConfig = ChunkSetupConfig(
            chunk_name=chunk["name"],
            image_directory=data_directory / Path(chunk["image_directory"]),
            camera_file=data_directory / Path(chunk["camera_file"]),
            camera_config=Path(chunk["camera_config"]),
        )

        chunk_configs.append(chunk_config)

    return Ok(ProjectSetupConfig(document=document_config, chunks=chunk_configs))


def log_project_setup(data: ProjectSetupData) -> None:
    """TODO"""

    logger.info("")
    logger.info("Project setup data:")
    logger.info(f" - Document: {data.document}")
    for chunk in data.chunks:
        chunk_info: str = f"Name: {chunk.chunk_name}"
        camera_info: str = f"Cameras: {len(chunk.cameras)}"
        image_info: str = f"Images: {chunk.image_registry.count}"
        reference_info: str = f"References: {chunk.reference_registry.count}"

        logger.info(f" - {chunk_info}, {camera_info}, {reference_info}, {image_info}")


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
        config.image_directory,
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
        document: Document = create_document()
        result: Result[Path, str] = save_document(document, config.document.path)
        if result.is_err():
            logger.error(f"failed to create document: {config.document.path}")
    else:
        document: Document = load_document(config.document.path).unwrap()

    return ProjectSetupData(document, chunks)


def on_task_success(data: ProjectSetupData) -> None:
    """Handler that is invoked when the setup task is successful."""
    result: Result[Path, str] = save_document(data.document)

    match result:
        case Ok(path):
            logger.info(f"saved document: {path}")
        case Err(error_message):
            logger.error(error_message)


def on_task_failure(data: ProjectSetupData) -> None:
    """Handler that is invoked when the setup task is a failure."""
    
    raise NotImplementedError("on_task_failure is not implemented")


def invoke_project_setup(command: Command) -> None:
    """Invokes an project setup task. The function involves a workflow of processing 
    arguments, creating configurations, loading data, and injecting the data in 
    the project chunks."""

    parse_result: Result[Namespace, str] = parse_project_setup_arguments(command.arguments)
    if parse_result.is_err():
        logger.error(parse_result.err())
        return

    namespace: Namespace = parse_result.ok()

    config_result: Result[ProjectSetupConfig, str] = create_project_setup_config(
        namespace.document,
        namespace.new,
        namespace.data_directory,
        namespace.chunk_config,
    )

    if config_result.is_err():
        logger.error(config_result.err())
        return

    config: ProjectSetupConfig = config_result.ok()

    # TODO: Validate config
    data: ProjectSetupData = prepare_project_setup_data(config)

    result: Result[None, str] = execute_project_setup(data)

    match result:
        case Ok(None):
            on_task_success(data)
        case Err(error):
            on_task_failure(error)
