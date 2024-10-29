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
@click.option("--colors", type=Path)
@click.option("--ranges", type=Path)
@click.option("--normals", type=Path)
def export_cameras(
    source: Path,
    destination: Path,
    target: str,
    colors: Path | None = None,
    ranges: Path | None = None,
    normals: Path | None = None,
) -> None:
    """Exports camera data from the backend.

    :arg source:            backend project source
    :arg destination:       export destination
    :arg target:            target group label
    :arg colors:            album of color images
    :arg ranges:            album of range images
    :arg normals:           album of normal images
    """

    assert source.exists(), f"source {source} does not exist"
    assert (
        destination.parent.exists()
    ), f"destination {destination} does not exist"

    # Load backend and get project information
    metashape.load_project(source).unwrap()
    _url: str = metashape.get_project_url().unwrap()

    cameras: CameraGroup = retrieve_camera_group(target).unwrap()

    if colors is not None:
        image_sources: dict[str, Path] = {
            ImageType.COLOR: Path(colors) if colors else None,
            ImageType.RANGE: Path(ranges) if ranges else None,
            ImageType.NORMAL: Path(normals) if normals else None,
        }
        images: dict[ImageType, Resources] = retrieve_images(
            image_sources
        ).unwrap()
    else:
        images = None

    export_camera_group(destination, cameras, images)


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


def retrieve_images(
    image_sources: Mapping[ImageType, str | Path]
) -> Result[ImageGroups, str]:
    """Retrieve images from sources."""

    image_tags: dict[ImageType, list[str]] = {
        image_type: ["image", str(image_type)] for image_type in image_sources
    }

    manager: ResourceManager = collect_image_resources(
        image_sources, image_tags
    )

    image_groups: ImageGroups = {
        image_type: manager.query_tags(tags)
        for image_type, tags in image_tags.items()
    }

    return Ok(image_groups)


def collect_image_resources(
    directories: Mapping[ImageType, str | Path],
    tags: Mapping[ImageType, list[str]],
) -> ResourceManager:
    """Collects image resources and adds them to a manager."""
    image_manager: ResourceManager = ResourceManager()

    # Find file handles
    image_files: dict[ImageType, list[Path]] = {
        image_type: list_directory(directory, IMAGE_FILE_PATTERN)
        for image_type, directory in directories.items()
    }

    # Create resources out of the file handles
    for image_type, files in image_files.items():
        resources: Resources = [
            create_resource(path) for path in files if path.exists()
        ]

        if len(resources) == 0:
            logger.warning(f"no resources for type: {image_type}")

        image_manager.add_resources(resources, tags=tags.get(image_type))

    return image_manager


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
