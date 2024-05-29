"""Entrypoint for project setup / initialization."""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from loguru import logger
from result import Ok, Err, Result

from benthoscan.project import Chunk, Document, save_document
from benthoscan.runtime import Command

from .config import create_project_config
from .setup import prepare_project_data


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


def invoke_project_setup(command: Command) -> None:
    """Invokes an project setup task. The function involves a workflow of 
    processing arguments, creating configurations, loading data, and 
    injecting the data in the project chunks."""

    parse_result: Result[Namespace, str] = parse_project_arguments(command.arguments)
    if parse_result.is_err():
        logger.error(parse_result.err())
        return

    namespace: Namespace = parse_result.ok()

    config_result: Result[ProjectConfig, str] = create_project_config(
        namespace.document,
        namespace.new,
        namespace.data_directory,
        namespace.chunk_config,
    )

    if config_result.is_err():
        logger.error(config_result.err())
        return

    config: ProjectConfig = config_result.ok()

    # TODO: Validate config - if the validation fails, stop the process

    # Execute task
    project_data: ProjectSetupData = prepare_project_data(config)
