"""Entrypoint for invoking project setup / initialization tasks from the command-line interface."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypeAlias

import click
import polars as pl

from mynd.io import read_config, read_data_frame

from mynd.tasks.ingestion.metadata import ingest_metadata_locally

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


# NOTE: Temporary - remove backend from
from ..backend import metashape as backend


@click.group(chain=True)
@click.pass_context
def ingestion(context: click.Context) -> None:
    """Command-line interface for ingesting data into the backend."""

    context.ensure_object(dict)


@dataclass(frozen=True)
class CameraIngestionBundle:
    """Class representing a camera ingestion bundle."""

    target: str
    cameras: pl.DataFrame
    metadata: pl.DataFrame
    config: dict


CameraIngestionInput: TypeAlias = tuple[str, Path, Path, Path]


def prepare_camera_bundles(
    context: click.Context,
    parameter: str,
    items: tuple[CameraIngestionInput],
) -> None:
    """Ingests camera data into the backend."""

    # TODO: Add validation of existing project if the create new option is selected

    raise NotImplementedError("prepare_camera_bundles is not implemented")


@ingestion.command()
@click.argument("source", type=Path)
@click.argument("destination", type=Path)
@click.option(
    "--bundle",
    "bundles",
    type=CameraIngestionInput,  # label, cameras, images, metadata
    multiple=True,
    callback=prepare_camera_bundles,
)
def ingest_cameras(
    source: Path,
    destination: Path,
    bundles: Optional[list[CameraIngestionBundle]] = None,
) -> None:
    """Ingests a group of cameras into the backend."""

    assert source.exists(), "source does not exist"
    assert destination.exists(), "destination does not exist"

    if source == destination:
        raise ValueError("source and destination cannot be the same")

    # TODO: Add hook for camera references
    # TODO: Add hook for camera metadata

    logger.info(f"Source:           {source}")
    logger.info(f"Destination:      {destination}")
    logger.info(f"Bundles:          {bundles}")

    # backend.ingestion_services.request_project_ingestion()

    raise NotImplementedError("ingest_cameras is not implemented")


@dataclass(frozen=True)
class MetadataIngestionBundle:
    """Class representing a metadata ingestion bundle."""

    target: str
    metadata: pl.DataFrame
    config: dict


MetadataIngestionInput: TypeAlias = tuple[str, Path, Path]


def prepare_metadata_bundles(
    context: click.Context,
    parameter: str,
    items: tuple[MetadataIngestionInput],
) -> list[MetadataIngestionBundle]:
    """Prepares pairs of targets and metadata sources."""

    bundles: list[MetadataIngestionBundle] = list()

    for target, metadata, config in items:

        if not metadata.exists():
            raise ValueError(f"metadata file does not exist: {metadata}")

        if not config.exists():
            raise ValueError(f"config file does not exist: {config}")

        bundles.append(
            MetadataIngestionBundle(
                target=target,
                metadata=read_data_frame(metadata).unwrap(),
                config=read_config(config).unwrap(),
            )
        )

    return bundles


@ingestion.command()
@click.argument("source", type=Path)
@click.argument("destination", type=Path)
@click.option(
    "--bundle",
    "bundles",
    type=(str, Path, Path),
    multiple=True,
    callback=prepare_metadata_bundles,
)
@click.pass_context
def ingest_metadata(
    context: click.Context,
    source: Path,
    destination: Path,
    bundles: Optional[list[MetadataIngestionBundle]] = None,
) -> None:
    """Ingest camera metadata locally. If no target group is given, the backend
    will try to target any group."""

    if source == destination:
        raise ValueError("source and destination cannot be the same")

    # TODO: If source and destination is provided - invoke local workflow
    if not bundles:
        raise ValueError("missing metadata ingestion bundles")

    if not source.exists():
        raise ValueError(f"source does not exist: {source}")

    if not destination.parent.exists():
        raise ValueError(
            f"destination directory does not exist: {destination.parent}"
        )

    match backend.load_project(source):
        case Ok(None):
            pass
        case Err(message):
            logger.error(message)
            return

    ingestion_results: dict[str, Result] = {
        bundle.target: ingest_metadata_locally(
            metadata=bundle.metadata, config=bundle.config, target=bundle.target
        )
        for bundle in bundles
    }

    logger.info("")
    for target, result in ingestion_results.items():
        handle_ingestion_result(target, result)
    logger.info("")

    match backend.save_project(destination):
        case Ok(path):
            logger.info(f"saved project successfully: {path}")
        case Err(message):
            logger.error(message)
            return


def handle_ingestion_result(name: str, result: Result[None, str]) -> None:
    """Callback to handle ingestion result."""
    match result:
        case Ok(None):
            logger.info(f"ingestion succeeded: {name}")
        case Err(error):
            logger.error(f"ingestion failed: {name}, {error}")
