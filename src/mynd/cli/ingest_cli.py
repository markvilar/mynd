"""Entrypoint for invoking project setup / initialization tasks from the command-line interface."""

from pathlib import Path
from typing import Optional

import click
import polars as pl

from ..collections import CameraGroup
from ..io import read_config, read_data_frame
from ..tasks.ingestion.metadata import map_metadata_to_cameras
from ..utils.log import logger
from ..utils.result import Ok, Err, Result


# NOTE: Temporary - remove backend from
from ..backend import metashape as backend


GroupID = CameraGroup.Identifier


@click.group(chain=True)
@click.pass_context
def ingestion(context: click.Context) -> None:
    """Command-line interface for ingesting data into the backend."""

    context.ensure_object(dict)


def prepare_project_callback(
    project: str, camera: str, images: str, create_new: bool
) -> None:
    """Ingests camera data into the backend."""

    # TODO: Add validation of existing project if the create new option is selected

    raise NotImplementedError("prepare_ingest is not implemented")


def convert_to_pathlib(
    context: click.Context, parameter: str, value: click.Path
) -> Path:
    """Converts a path from click to pathlib."""
    return Path(value)


def prepare_data_frame(
    context: click.Context, parameter: str, path: click.Path
) -> Optional[pl.DataFrame]:
    """Prepares a data frame by loading it from file."""
    match read_data_frame(Path(path)):
        case Ok(data):
            return data
        case Err(message):
            logger.error(message)
            return None


def prepare_config(
    context: click.Context, parameter: str, path: click.Path
) -> Optional[dict]:
    """Prepares a configuration by loading it from file."""
    match read_config(Path(path)):
        case Ok(config):
            return config
        case Err(message):
            logger.error(message)
            return None


@ingestion.command()
@click.argument("project", type=click.Path(), callback=convert_to_pathlib)
@click.argument(
    "cameras", type=click.Path(exists=True), callback=convert_to_pathlib
)
@click.argument(
    "images", type=click.Path(exists=True), callback=convert_to_pathlib
)
@click.argument(
    "config", type=click.Path(exists=True), callback=convert_to_pathlib
)
@click.option("--label", type=str, help="camera group label")
def ingest_cameras(
    project: Path, cameras: Path, images: Path, config: Path
) -> None:
    """Ingests a group of cameras into the backend."""

    # TODO: Add hook for camera references
    # TODO: Add hook for camera metadata

    logger.info("Destination")
    logger.info(f"Camera: {cameras}")
    logger.info(f"Images: {images}")

    cameras: pl.DataFrame = read_data_frame(cameras).unwrap()
    config: dict = read_config(config).unwrap()

    backend.ingestion_services.request_project_ingestion()

    raise NotImplementedError("ingest_cameras is not implemented")


@ingestion.command()
@click.argument(
    "metadata",
    type=click.Path(exists=True),
    callback=prepare_data_frame,
)
@click.argument("config", type=click.Path(exists=True), callback=prepare_config)
@click.option("--target", type=str, help="target camera group")
@click.option(
    "--source", type=click.Path(exists=True), callback=convert_to_pathlib
)
@click.option("--destination", type=click.Path(), callback=convert_to_pathlib)
@click.pass_context
def ingest_metadata(
    context: click.Context,
    metadata: pl.DataFrame,
    config: dict,
    target: Optional[str] = None,
    source: Optional[Path] = None,
    destination: Optional[Path] = None,
) -> None:
    """Ingest camera metadata locally. If no target group is given, the backend
    will try to target any group."""

    # TODO: If source and destination is provided - invoke local workflow

    match backend.load_project(source):
        case Ok(None):
            pass
        case Err(message):
            logger.error(message)
            return

    match ingest_metadata_locally(
        metadata=metadata, config=config, target=target
    ):
        case Ok(None):
            logger.info("ingested metadata!")
        case Err(message):
            logger.error(message)
            return

    match backend.save_project(destination):
        case Ok(path):
            logger.info(f"saved project successfully: {path}")
        case Err(message):
            logger.error(message)
            return


def ingest_metadata_locally(
    metadata: pl.DataFrame, config: dict, target: Optional[str] = None
) -> Result[None, str]:
    """Ingest camera metadata via API. If no target group is given, the backend
    will try to target any group."""

    table_map: dict = config.get("table_map")

    camera_metadata: dict[str, dict] = map_metadata_to_cameras(
        metadata,
        table_map.get("label_field"),
        table_map.get("data_fields"),
    )

    group_identifiers: list[GroupID] = backend.get_group_identifiers().unwrap()
    group_labels: dict[str, GroupID] = {
        identifier.label: identifier for identifier in group_identifiers
    }

    if not target:
        target_identifiers: list[GroupID] = group_identifiers
    elif target in group_labels:
        target_identifiers: list[GroupID] = [group_labels.get(target)]
    else:
        target_identifiers: list[GroupID] = None

    results: dict[GroupID, Result] = {
        identifier: backend.camera_services.update_camera_metadata(
            identifier, camera_metadata
        )
        for identifier in target_identifiers
    }

    for identifier, result in results.items():
        match result:
            case Ok(_statistics):
                pass
            case Err(message):
                return Err(message)

    return Ok(None)
