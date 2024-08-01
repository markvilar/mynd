"""Module for invoking registration tasks from the command-line interface."""

import tempfile

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from result import Ok, Err, Result

from ..backends import metashape as backend
from ..runtime import Command, load_environment
from ..registration import PointCloudLoader
from ..utils.log import logger

from ..tasks.registration import (
    RegistrationTaskConfig,
    execute_point_cloud_registration,
)


def parse_task_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """Parses command-line arguments for a registration task."""
    parser = ArgumentParser()

    parser.add_argument("document", type=Path, help="document path")
    parser.add_argument(
        "--include", type=str, nargs="+", help="chunk labels to include"
    )
    parser.add_argument(
        "--overwrite",
        type=bool,
        action=BooleanOptionalAction,
        help="chunk labels to select",
    )

    namespace: Namespace = parser.parse_args(arguments)

    if not namespace:
        return Err(f"failed to parse arguments: {arguments}")

    return Ok(namespace)


DenseResponseData = dict[int, PointCloudLoader]


def configure_registration_task(
    document_path: Path, overwrite: bool
) -> Result[RegistrationTaskConfig, str]:
    """TODO"""

    environment: Environment = load_environment()
    tempfile.tempdir = environment.cache_directory

    response: Result[DenseResponseData, str] = backend.request_dense_models(
        document_path,
        environment.cache_directory,
        overwrite,
    )

    match response:
        case Ok(loaders):
            return Ok(RegistrationTaskConfig(loaders))
        case Err(message):
            logger.error(message)
        case _:
            raise NotImplementedError("invalid dense model response")


def on_task_success(config: RegistrationTaskConfig) -> None:
    """Handler that is called if the task is successful."""
    raise NotImplementedError("on_task_success is not implemented")


def on_task_failure(config: RegistrationTaskConfig, message: str) -> None:
    """Handler that is called if the task is unsuccessful."""
    logger.error(f"registration task failed: {message}")


def invoke_registration_task(command: Command) -> None:
    """Invokes a registration task by requesting point clouds from the backend.
    If point clouds are provided, the registration task is executed."""

    namespace: Namespace = parse_task_arguments(command.arguments).unwrap()

    config: RegistrationTaskConfig = configure_registration_task(
        document_path=namespace.document,
        overwrite=namespace.overwrite,
    ).unwrap()

    # TODO: Finalize execution of registration task
    result: Result[None, str] = execute_point_cloud_registration(config)

    # TODO: Send registration results in a request to the backend
    match result:
        case Ok(None):
            on_task_success(config)
        case Err(message):
            on_task_failure(config, message)
