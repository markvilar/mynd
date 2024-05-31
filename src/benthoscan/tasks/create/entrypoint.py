"""Entrypoint for project setup / initialization."""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from loguru import logger
from result import Ok, Err, Result

from benthoscan.io import read_toml
from benthoscan.runtime import Command

from .config_types import ChunkSetupConfig, DocumentSetupConfig, ProjectSetupConfig
from .setup import prepare_project_setup_data
from .worker import setup_project_data


def parse_project_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """Creates an argument parser and parses the given arguments."""
    parser = ArgumentParser()

    # Document arguments
    parser.add_argument("document", type=Path, help="document path")
    parser.add_argument("data_directory", type=Path, help="data directory")
    parser.add_argument("--new", action=BooleanOptionalAction, help="create new document")

    # Chunk / data arguments
    parser.add_argument("chunk_config", type=Path, default=None, help="data configuration file")
    
    namespace = parser.parse_args(arguments)

    if not namespace:
        return Err(f"failed to parse arguments: {arguments}")

    return Ok(namespace)


def create_project_setup_config(
    document: Path, 
    create_new: bool, 
    data_directory: Path, 
    chunk_config: Path
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
            chunk_name = chunk["name"],
            image_directory = data_directory / Path(chunk["image_directory"]),
            camera_file = data_directory / Path(chunk["camera_file"]),
            camera_config = Path(chunk["camera_config"])
        )

        chunk_configs.append(chunk_config)

    return Ok(ProjectSetupConfig(document=document_config, chunks=chunk_configs))


def invoke_project_setup(command: Command) -> None:
    """Invokes an project setup task. The function involves a workflow of 
    processing arguments, creating configurations, loading data, and 
    injecting the data in the project chunks."""

    parse_result: Result[Namespace, str] = parse_project_arguments(command.arguments)
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

    logger.info("")
    logger.info("Project setup data:")
    logger.info(f" - Document: {data.document}")
    logger.info(" - Chunks:")
    for chunk in data.chunks:
        chunk_info: str = f"Name: {chunk.chunk_name}" 
        camera_info: str = f"Cameras: {len(chunk.cameras)}"
        image_info: str = f"Images: {chunk.image_registry.count}"
        reference_info: str = f"References: {chunk.reference_registry.count}"

        logger.info(f"   - {chunk_info}, {camera_info}, {reference_info}, {image_info}")

    setup_project_data(data)
