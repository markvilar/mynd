"""Module for camera related CLI functionality."""

from pathlib import Path
from typing import Optional

import click

from ..backend import metashape
from ..camera import Camera
from ..collections import CameraGroup
from ..image import ImageType

from ..tasks.export_cameras import manage_camera_group_export

from ..utils.log import logger
from ..utils.result import Ok, Err, Result


CameraID = Camera.Identifier
GroupID = CameraGroup.Identifier


IMAGE_PATTERN: str = "*.tiff"


@click.group()
@click.pass_context
def camera_cli(context: click.Context) -> None:
    """CLI for camera specific tasks."""
    context.ensure_object(dict)


@camera_cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("destination", type=click.Path())
@click.argument("target", type=str)
@click.option(
    "--stereo",
    is_flag=True,
    show_default=True,
    default=False,
    help="Export stereo geometry",
)
@click.option("--colors", type=click.Path(exists=True))
@click.option("--ranges", type=click.Path(exists=True))
@click.option("--normals", type=click.Path(exists=True))
def export_cameras(
    source: str,
    destination: str,
    target: str,
    stereo: bool,
    colors: Optional[click.Path],
    ranges: Optional[click.Path],
    normals: Optional[click.Path],
) -> None:
    """Exports camera data from the backend."""

    # Prepare command-line arguments
    source: Path = Path(source)
    destination: Path = Path(destination)

    image_sources: dict[str, Path] = {
        ImageType.COLOR: Path(colors) if colors else None,
        ImageType.RANGE: Path(ranges) if ranges else None,
        ImageType.NORMAL: Path(normals) if normals else None,
    }

    assert source.exists(), f"source {source} does not exist"
    assert (
        destination.parent.exists()
    ), f"destination {destination} does not exist"

    # Load backend and get project information
    metashape.load_project(source).unwrap()
    url: str = metashape.get_project_url().unwrap()

    logger.info(f"Project: {url}")

    # NOTE: Basic export setup is to export basic camera data
    # (references, attributes, sensors)
    # NOTE: Add option to export stereo calibrations
    # NOTE: Add option to export images (range and normal maps)

    match retrieve_camera_group(target):
        case Ok(cameras):
            manage_camera_group_export(destination, cameras, image_sources)
        case Err(message):
            logger.error(message)
            return
        case _:
            raise NotImplementedError


def retrieve_camera_group(target_label: str) -> Result[CameraGroup, str]:
    """Gets the camera group from the backend."""

    group_identifiers: list[GroupID] = (
        metashape.get_group_identifiers().unwrap()
    )

    label_to_group: dict[str, GroupID] = {
        identifier.label: identifier for identifier in group_identifiers
    }

    if target_label not in label_to_group:
        return Err(
            f"missing target group {target_label}, found {*label_to_group,}"
        )

    target: GroupID = label_to_group.get(target_label)

    attributes: CameraGroup.Attributes = metashape.get_camera_attributes(
        target
    ).unwrap()
    estimated_references: CameraGroup.References = (
        metashape.get_estimated_camera_references(target).unwrap()
    )
    prior_references: CameraGroup.References = (
        metashape.get_prior_camera_references(target).unwrap()
    )

    return Ok(
        CameraGroup(target, attributes, estimated_references, prior_references)
    )
