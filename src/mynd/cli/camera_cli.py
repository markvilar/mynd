"""Module for camera related CLI functionality."""

import glob

from collections.abc import Iterable
from pathlib import Path
from typing import Optional

import click

from ..backend import metashape
from ..camera import Camera
from ..collections import CameraGroup

from ..tasks.export_cameras import manage_camera_group_export

from ..utils.log import logger


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
        "colors": Path(colors) if colors else None,
        "ranges": Path(ranges) if ranges else None,
        "normals": Path(normals) if normals else None,
    }

    assert source.exists(), f"source {source} does not exist"
    assert (
        destination.parent.exists()
    ), f"destination {destination} does not exist"

    # Load backend and get project information
    metashape.load_project(source).unwrap()
    url: str = metashape.get_project_url().unwrap()

    logger.info(f"Project: {url}")

    group_identifiers: list[GroupID] = (
        metashape.get_group_identifiers().unwrap()
    )
    target_group: Optional[GroupID] = get_target_group(
        target, group_identifiers
    )

    if target_group is None:
        group_labels: list[str] = [
            identifier.label for identifier in group_identifiers
        ]
        logger.error(f"could not find target group: {target}")
        logger.error(f"groups in project are: {*group_labels,}")
        return

    cameras: CameraGroup = get_camera_group(target_group)

    if not any(
        [image_source is None for image_source in image_sources.values()]
    ):
        images: dict[str, list[Path]] = get_image_files(image_sources)
    else:
        images = None

    # NOTE: Basic export setup is to export basic camera data
    # (references, attributes, sensors)
    # NOTE: Add option to export stereo calibrations
    # NOTE: Add option to export images (range and normal maps)

    manage_camera_group_export(destination, cameras, images)


def get_camera_group(identifier: GroupID) -> CameraGroup:
    """Gets the camera group from the backend."""

    attributes: CameraGroup.Attributes = metashape.get_camera_attributes(
        identifier
    ).unwrap()
    estimated_references: CameraGroup.References = (
        metashape.get_estimated_camera_references(identifier).unwrap()
    )
    prior_references: CameraGroup.References = (
        metashape.get_prior_camera_references(identifier).unwrap()
    )

    return CameraGroup(
        identifier, attributes, estimated_references, prior_references
    )


def get_image_files(sources: dict[str, Path]) -> dict[str, Iterable[Path]]:
    """Retrieves image paths from the sources."""

    images: dict[str, list[Path]] = {
        name: [Path(path) for path in glob.glob(f"{source}/{IMAGE_PATTERN}")]
        for name, source in sources.items()
    }

    return images


def get_target_group(
    target: str, identifiers: list[GroupID]
) -> Optional[GroupID]:
    """Returns a group identifier if it matches the target label, and none otherwise."""

    matches: list[GroupID] = [
        identifier for identifier in identifiers if identifier.label == target
    ]

    if not matches:
        return None

    return matches[0]
