"""Entrypoint for invoking project setup / initialization tasks from the command-line interface."""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from ..io import read_config
from ..runtime import Command
from ..project import DocumentOptions, ProjectData
from ..utils.log import logger
from ..utils.result import Ok, Err, Result

from ..tasks.ingestion import CameraGroupConfig, ProjectConfig
from ..tasks.ingestion import execute_project_setup

# TODO: Add functionality to swap backends
from ..backends import metashape as backend


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


def configure_project_data(
    document: Path, create_new: bool, data_directory: Path, chunk_config: Path
) -> Result[ProjectConfig, str]:
    """Creates a project configuration consisting of document and chunk configurations."""

    # TODO: Configure input data from command-line arguments

    document_options: DocumentOptions = DocumentOptions(document, create_new)

    read_result: Result[dict, str] = read_config(chunk_config)
    if read_result.is_err():
        return read_result

    config: dict = read_result.ok()

    groups = config.get("chunk", None)
    if not groups:
        return Err("missing key 'chunk' in configuration file")

    camera_groups: list[CameraGroupConfig] = list()
    for group in groups:
        camera_group: CameraGroupConfig = CameraGroupConfig(
            name=group["name"],
            image_directory=data_directory / Path(group["image_directory"]),
            camera_data=data_directory / Path(group["camera_data"]),
            camera_config=Path(group["camera_config"]),
        )

        camera_groups.append(camera_group)

    return Ok(
        ProjectConfig(document_options=document_options, camera_groups=camera_groups)
    )


def on_task_success(config: ProjectConfig, path: Path) -> None:
    """Handler that is invoked when the setup task is successful."""

    logger.info(f"ingested data successfully: {path}")


def on_task_failure(config: ProjectConfig, message: str) -> None:
    """Handler that is invoked when the setup task is a failure."""

    logger.error(f"failed to set up project: {message}")


def invoke_project_setup(command: Command) -> None:
    """Invokes a project setup task. The function involves a workflow of processing
    arguments, creating configurations, loading data, and injecting the data in
    the project chunks."""

    parse_result: Result[Namespace, str] = parse_project_setup_arguments(
        command.arguments
    )
    if parse_result.is_err():
        logger.error(parse_result.err())
        return

    namespace: Namespace = parse_result.ok()

    config: ProjectConfig = configure_project_data(
        namespace.document,
        namespace.new,
        namespace.data_directory,
        namespace.chunk_config,
    ).unwrap()

    # TODO: Prepare data for ingestion
    result: Result[ProjectData, str] = execute_project_setup(config)

    match result:
        case Err(message):
            on_task_failure(config, message)

    project_data: ProjectData = result.ok()
    response: Result[Path, str] = backend.request_data_ingestion(project_data)

    match response:
        case Ok(path):
            on_task_success(config, path)
        case Err(message):
            on_task_failure(config, message)
