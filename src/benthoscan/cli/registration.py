"""Module for invoking registration tasks from the command-line interface."""

import tempfile

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from result import Ok, Err, Result

from benthoscan.io import read_toml
from benthoscan.project import Document, load_document, save_document
from benthoscan.runtime import Command, load_environment
from benthoscan.spatial import write_point_cloud
from benthoscan.utils.log import logger


from benthoscan.tasks.registration import (
    RegistrationTaskConfig,
    execute_point_cloud_registration,
)


def parse_task_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """TODO"""
    parser = ArgumentParser()

    parser.add_argument("document", type=Path, help="document path")
    parser.add_argument("--select", type=str, nargs="+", help="chunk labels to select")

    namespace = parser.parse_args(arguments)

    if not namespace:
        return Err(f"failed to parse arguments: {arguments}")

    return Ok(namespace)


def configure_registration_task(
    path: Path, overwrite: bool
) -> Result[RegistrationTaskConfig, str]:
    """TODO"""

    load_result: Result[Document, str] = load_document(path)
    environment: Environment = load_environment()
    tempfile.tempdir = environment.cache_directory

    match load_result:
        case Err(error):
            return Err(error)
        case Ok(document):
            point_cloud_files: dict[str, Path] = export_point_clouds(
                document,
                environment.cache_directory,
                overwrite,
            )
            return Ok(RegistrationTaskConfig(point_cloud_files))


def export_point_clouds(
    document: Document,
    cache_directory: Path,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Export point clouds from a document to a cache dirctory."""

    point_cloud_files: dict[str, Path] = dict()
    for chunk in document.chunks:
        if not chunk.enabled:
            continue

        output_path: Path = cache_directory / f"{chunk.label}.ply"

        if output_path.exists() and not overwrite:
            file_path: Path = output_path
        else:
            file_path: Path = write_point_cloud(chunk, path=output_path).unwrap()

        point_cloud_files[chunk.label] = file_path

    return point_cloud_files


def on_task_success(config) -> None:
    """Handler that is called when the task is successful."""
    raise NotImplementedError("on_task_success is not implemented")


def on_task_failure(config, error) -> None:
    """Handler that is called when the task is unsuccessful."""
    raise NotImplementedError("on_task_failure is not implemented")


def invoke_registration_task(command: Command) -> None:
    """TODO"""

    namespace: Namespace = parse_task_arguments(command.arguments).unwrap()

    # TODO: Move data exporting to backend
    """
    config: RegistrationTaskConfig = configure_registration_task(
        path = namespace.document,
        overwrite = False,
    ).unwrap()
    """

    config: RegistrationTaskConfig = RegistrationTaskConfig(
        {
            "qdc5ghs3_20100430_024508": Path(".cache/qdc5ghs3_20100430_024508.ply"),
            "qdc5ghs3_20120501_033336": Path(".cache/qdc5ghs3_20120501_033336.ply"),
            "qdc5ghs3_20130405_103429": Path(".cache/qdc5ghs3_20130405_103429.ply"),
            "qdc5ghs3_20210315_230947": Path(".cache/qdc5ghs3_20210315_230947.ply"),
        }
    )

    # TODO: Send registration results to backend
    result: Result[None, str] = execute_point_cloud_registration(config)
