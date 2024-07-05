"""Module for invoking registration tasks from the command-line interface."""

import tempfile

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from functools import partial
from pathlib import Path

from result import Ok, Err, Result

from benthoscan.io import read_toml
from benthoscan.project import Document, load_document, save_document
from benthoscan.runtime import Command, load_environment
from benthoscan.registration import (
    read_point_cloud,
    write_point_cloud,
    PointCloudLoader,
)
from benthoscan.utils.log import logger


from benthoscan.tasks.registration import (
    RegistrationTaskConfig,
    execute_point_cloud_registration,
)


def parse_task_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """TODO"""
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


def get_point_cloud_loaders_from_document(
    document: Document,
    cache: Path,
    overwrite: bool,
) -> dict[int, PointCloudLoader]:
    """TODO"""

    point_cloud_files: dict[int, Path] = dict()
    for chunk in document.chunks:
        if not chunk.enabled:
            continue

        output_path: Path = cache / f"{chunk.label}.ply"

        if output_path.exists() and not overwrite:
            file_path: Path = output_path
        else:
            file_path: Path = write_point_cloud(chunk, path=output_path).unwrap()

        point_cloud_files[chunk.key] = file_path

    point_cloud_loaders: dict[int, PointCloudLoader] = {
        key: partial(read_point_cloud, path=path)
        for key, path in point_cloud_files.items()
    }

    return point_cloud_loaders


# TODO: Move point cloud loader request to backend
def request_point_cloud_loaders(
    document_path: Path,
    cache_directory: Path,
    overwrite: bool,
) -> Result[dict[int, PointCloudLoader], str]:
    """Export point clouds from a document to a cache dirctory."""

    load_result: Result[Document, str] = load_document(document_path)

    match load_result:
        case Ok(document):
            loaders: dict[int, PointCloudLoader] = (
                get_point_cloud_loaders_from_document(
                    document,
                    cache_directory,
                    overwrite,
                )
            )
            return Ok(loaders)
        case Err(error):
            return Err(error)
        case _:
            raise NotImplementedError("invalid result case")


def configure_registration_task(
    document_path: Path, overwrite: bool
) -> Result[RegistrationTaskConfig, str]:
    """TODO"""

    environment: Environment = load_environment()
    tempfile.tempdir = environment.cache_directory

    # TODO: Move to backend
    result: Result = request_point_cloud_loaders(
        document_path,
        environment.cache_directory,
        overwrite,
    )

    match result:
        case Ok(loaders):
            return Ok(RegistrationTaskConfig(loaders))
        case Err(message):
            logger.error(message)
        case _:
            raise NotImplementedError("invalid result case")


def on_task_success(config: RegistrationTaskConfig) -> None:
    """Handler that is called when the task is successful."""
    raise NotImplementedError("on_task_success is not implemented")


def on_task_failure(config: RegistrationTaskConfig, error: str) -> None:
    """Handler that is called when the task is unsuccessful."""
    raise NotImplementedError("on_task_failure is not implemented")


def invoke_registration_task(command: Command) -> None:
    """TODO"""

    namespace: Namespace = parse_task_arguments(command.arguments).unwrap()

    # TODO: Move data exporting to backend
    config: RegistrationTaskConfig = configure_registration_task(
        document_path=namespace.document,
        overwrite=namespace.overwrite,
    ).unwrap()

    # TODO: Send registration results to backend
    result: Result[None, str] = execute_point_cloud_registration(config)

    match result:
        case Ok(None):
            on_task_success(config)
        case Err(error):
            on_task_failure(config, error)
