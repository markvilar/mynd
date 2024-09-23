"""Entrypoint for invoking project setup / initialization tasks from the command-line interface."""

from pathlib import Path

import click

from ..backend import metashape as backend
from ..io import read_config
from ..utils.log import logger


@click.group(chain=True)
@click.pass_context
def ingestion(context: click.Context) -> None:
    """Command-line interface for ingesting data into the backend."""

    context.ensure_object(dict)


@ingestion.command()
@click.argument("project", type=click.Path())
@click.option("--create-new", is_flag=True, show_default=True, default=False, help="create new project")
def prepare_ingest(project: str, camera: str, images: str, create_new: bool) -> None:
    """Ingests camera data into the backend."""

    # TODO: Add validation of existing project if the create new option is selected

    raise NotImplementedError("prepare_ingest is not implemented")


@ingestion.command()
@click.argument("cameras", type=click.Path(exists=True))
@click.argument("images", type=click.Path(exists=True))
@click.argument("config", type=click.Path(exists=True))
@click.option("--label", type=str, help="camera group label")
def ingest_cameras(cameras: click.Path, images: click.Path, config: click.Path) -> None:
    """Ingests a group of cameras into the backend."""

    cameras: Path = Path(cameras)
    images: Path = Path(images)

    logger.info(f"Camera: {cameras}")
    logger.info(f"Images: {images}")

    config: dict = read_config(config)

    backend.request_project_ingestion()

    raise NotImplementedError("ingest_cameras is not implemented")


def invoke_project_setup() -> None:
    """Invokes a data ingestion task."""
    raise NotImplementedError("invoke_project_setup is not implemented")
