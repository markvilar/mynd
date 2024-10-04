"""Entrypoint for invoking project setup / initialization tasks from the command-line interface."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click
import polars as pl

from ..backend import metashape as backend
from ..io import read_config, read_data_frame
from ..tasks.ingestion.ingest_metadata import map_metadata_to_cameras
from ..utils.log import logger
from ..utils.result import Ok, Err, Result


@click.group(chain=True)
@click.pass_context
def ingestion(context: click.Context) -> None:
    """Command-line interface for ingesting data into the backend."""

    context.ensure_object(dict)


@ingestion.command()
@click.argument("project", type=click.Path())
@click.option(
    "--create-new",
    is_flag=True,
    show_default=True,
    default=False,
    help="create new project",
)
def prepare_ingest(
    project: str, camera: str, images: str, create_new: bool
) -> None:
    """Ingests camera data into the backend."""

    # TODO: Add validation of existing project if the create new option is selected

    raise NotImplementedError("prepare_ingest is not implemented")


@ingestion.command()
@click.argument("cameras", type=click.Path(exists=True))
@click.argument("images", type=click.Path(exists=True))
@click.argument("config", type=click.Path(exists=True))
@click.option("--label", type=str, help="camera group label")
def ingest_cameras(
    cameras: click.Path, images: click.Path, config: click.Path
) -> None:
    """Ingests a group of cameras into the backend."""

    cameras: Path = Path(cameras)
    images: Path = Path(images)

    logger.info(f"Camera: {cameras}")
    logger.info(f"Images: {images}")

    config: dict = read_config(config)

    backend.request_project_ingestion()

    # TODO: Add hook to ingest metadata

    raise NotImplementedError("ingest_cameras is not implemented")


def prepare_data_frame(context: click.Context, parameter: str, path: click.Path) -> Optional[pl.DataFrame]:
    """Prepares a data frame by loading it from file."""
    match read_data_frame(Path(path)):
        case Ok(data):
            return data
        case Err(message):
            logger.error(message)
            return None


def prepare_config(context: click.Context, parameter: str, path: click.Path) -> Optional[dict]:
    """Prepares a configuration by loading it from file."""
    match read_config(Path(path)):
        case Ok(config):
            return config
        case Err(message):
            logger.error(message)
            return None


@ingestion.command()
@click.argument("metadata", type=click.Path(exists=True), callback=prepare_data_frame)
@click.argument("config", type=click.Path(exists=True), callback=prepare_config)
@click.option("--target", type=click.Path(exists=True))
def ingest_metadata(
    metadata: Optional[pl.DataFrame], 
    config: Optional[dict], 
    target: Optional[str]=None
) -> None:
    """Ingest metadata into camera groups. If no target group is given, the backend
    will try to target any group."""

    if metadata is None or config is None:
        return
    
    table_map: dict = config.get("table_map")

    camera_metadata: dict[str, dict] = map_metadata_to_cameras(
        metadata, 
        table_map.get("label_field"), 
        table_map.get("data_fields"),
    )

    raise NotImplementedError("ingest_metadata is not implemented")
