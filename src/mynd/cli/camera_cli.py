"""Module for camera related CLI functionality."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import click

from mynd.backend import metashape

from mynd.collections import GroupID, CameraGroup
from mynd.image import ImageType

from mynd.tasks.export_cameras import export_camera_group
from mynd.tasks.export_stereo import export_stereo_geometry

from mynd.utils.filesystem import (
    list_directory,
    create_resource,
    Resource,
    ResourceManager,
)

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


Resources = list[Resource]
ImageGroups = Mapping[ImageType, Resources]


IMAGE_FILE_PATTERN: str = "*.tiff"


@click.group()
@click.pass_context
def camera_cli(context: click.Context) -> None:
    """CLI for camera specific tasks."""
    context.ensure_object(dict)


@dataclass
class ExportCameraBundle:

    target: str
    colors: Path | None = None
    ranges: Path | None = None
    normals: Path | None = None


def prepare_camera_export_bundle(
    context: click.Context,
    parameter: str,
    items: tuple[str, Path, Path, Path],
) -> list[ExportCameraBundle]:
    """Prepares a camera export bundle."""

    for target, colors, ranges, normals in items:
        logger.info(f"Items:        {target}")
        logger.info(f"Colors:       {colors}")
        logger.info(f"Ranges:       {ranges}")
        logger.info(f"Normals:      {normals}")

    return None


@camera_cli.command()
@click.argument("source", type=Path)
@click.argument("destination", type=Path)
@click.argument("target", type=str)
def export_cameras(
    source: Path,
    destination: Path,
    target: str,
) -> None:
    """Exports camera data from the backend.

    :arg source:            backend project source
    :arg destination:       export destination
    :arg target:            target group label
    """

    assert source.exists(), f"source {source} does not exist"
    assert (
        destination.parent.exists()
    ), f"destination {destination} does not exist"

    # Load backend and get project information
    metashape.load_project(source).unwrap()
    _url: str = metashape.get_project_url().unwrap()

    cameras: CameraGroup = retrieve_camera_group(target).unwrap()

    export_camera_group(destination, cameras)


def retrieve_camera_group(target_label: str) -> Result[CameraGroup, str]:
    """Retrieves a camera group from the backend."""

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

    return metashape.camera_services.retrieve_camera_group(target)


# -----------------------------------------------------------------------------
# ---- Stereo export ----------------------------------------------------------
# -----------------------------------------------------------------------------


@camera_cli.command()
@click.argument("source", type=Path)
@click.argument("destination", type=Path)
@click.argument("matcher", type=Path)
@click.argument("target", type=str)
@click.option(
    "--visualize",
    is_flag=True,
    show_default=True,
    default=False,
    help="visualize geometry.",
)
@click.option(
    "--save-samples",
    is_flag=True,
    show_default=True,
    default=False,
    help="save geometry samples",
)
def export_stereo(
    source: Path,
    destination: Path,
    matcher: Path,
    target: str,
    visualize: bool,
    save_samples: bool,
) -> None:
    """Export stereo ranges and normals."""

    assert source.exists(), f"source does not exist: {source}"
    assert source.is_file(), f"source is not a file: {source}"
    assert destination.exists(), f"destination does not exist: {destination}"
    assert (
        destination.is_dir()
    ), f"destination is not a directory: {destination}"
    assert matcher.exists(), f"matcher does not exist: {matcher}"
    assert matcher.is_file(), f"matcher is not a file: {matcher}"

    metashape.load_project(source).unwrap()

    groups: dict[str, GroupID] = {
        group.label: group
        for group in metashape.get_group_identifiers().unwrap()
    }

    target: GroupID = groups.get(target)

    assert target is not None, f"could not find target group: {target}"

    match metashape.camera_services.retrieve_stereo_cameras(target):
        case Ok(stereo_groups):

            # TODO: Invoke export task for each stereo group
            for stereo_group in stereo_groups:
                export_stereo_geometry(
                    stereo_group,
                    destination,
                    matcher,
                    visualize,
                    save_samples,
                )

            pass
        case Err(message):
            logger.error(message)
            return
        case _:
            raise NotImplementedError("invalid stereo retrieval result")
