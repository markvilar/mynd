"""Entrypoint for invoking project setup / initialization tasks from the command-line interface."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypeAlias

import click
import polars as pl

from mynd.collections import CameraGroup
from mynd.io import read_config, read_data_frame
from mynd.tasks.ingestion.metadata import map_metadata_to_cameras
from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


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


@dataclass(frozen=True)
class MetadataIngestionBundle:
    """Class representing a metadata ingestion query."""

    target: str
    metadata: pl.DataFrame
    config: dict


MetadataIngestInput: TypeAlias = tuple[str, Path, Path]


def prepare_metadata_bundles(
    context: click.Context,
    parameter: str,
    items: tuple[MetadataIngestInput],
) -> list[MetadataIngestionBundle]:
    """Prepares pairs of targets and metadata sources."""

    queries: list[MetadataIngestionBundle] = list()

    for target, metadata, config in items:

        if not metadata.exists():
            raise ValueError(f"metadata file does not exist: {metadata}")

        if not config.exists():
            raise ValueError(f"config file does not exist: {config}")

        queries.append(
            MetadataIngestionBundle(
                target=target,
                metadata=read_data_frame(metadata).unwrap(),
                config=read_config(config).unwrap(),
            )
        )

    return queries


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
    "source",
    type=click.Path(exists=True),
    callback=convert_to_pathlib,
)
@click.argument("destination", type=click.Path(), callback=convert_to_pathlib)
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
        raise ValueError("")

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


def ingest_metadata_locally(
    metadata: pl.DataFrame,
    config: dict,
    target: str,
) -> Result[None, str]:
    """Ingest camera metadata via API. If no target group is given, the backend
    will try to target any group."""

    METADATA_CONFIG_KEY: str = "metadata"
    TABLE_MAP_CONFIG_KEY: str = "table_maps"

    if METADATA_CONFIG_KEY not in config:
        return Err(f"missing config entry: {METADATA_CONFIG_KEY}")

    metadata_config: dict = config.get("metadata")

    if TABLE_MAP_CONFIG_KEY not in metadata_config:
        return Err(f"missing metadata config entry: {TABLE_MAP_CONFIG_KEY}")

    table_maps: dict = metadata_config.get("table_maps")

    camera_metadata: dict[str, dict] = map_metadata_to_cameras(
        metadata,
        table_maps.get("label_field"),
        table_maps.get("data_fields"),
    )

    group_identifiers: list[GroupID] = backend.get_group_identifiers().unwrap()
    group_map: dict[str, GroupID] = {
        identifier.label: identifier for identifier in group_identifiers
    }

    if target not in group_map:
        return Err("did not find target group: {target}")

    target_group: GroupID = group_map.get(target)

    update_result: Result = backend.camera_services.update_camera_metadata(
        target_group, camera_metadata
    )

    return update_result


def handle_ingestion_result(name: str, result: Result[None, str]) -> None:
    """Callback to handle ingestion result."""
    match result:
        case Ok(None):
            logger.info(f"ingestion succeeded: {name}")
        case Err(error):
            logger.error(f"ingestion failed: {name}, {error}")
