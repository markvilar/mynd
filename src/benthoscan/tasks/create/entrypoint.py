"""Entrypoint for project setup / initialization."""

from loguru import logger
from result import Result

from benthoscan.project import Chunk, Document, save_document
from benthoscan.runtime import Command

from .arguments import parse_project_arguments, configure_project
from .loaders import prepare_project_data


def invoke_project_setup(command: Command) -> None:
    """Invokes an project setup task. The function involves a workflow of 
    processing arguments, creating configurations, loading data, and 
    injecting the data in the project chunks."""

    parse_result: Result[Namespace, str] = parse_project_arguments(command.arguments)
    if parse_result.is_err():
        logger.error(parse_result.err())
        return

    namespace: Namespace = parse_result.ok()

    config_result: Result[ProjectConfig, str] = configure_project(namespace)
    if config_result.is_err():
        logger.error(config_result.err())
        return

    config: ProjectConfig = config_result.ok()

    # TODO: Validate config - if the validation fails, stop the process

    # Execute task
    project_data: ProjectData = prepare_project_data(config)
