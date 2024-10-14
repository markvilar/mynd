"""Module for camera related CLI functionality."""

from collections.abc import Mapping
from pathlib import Path
from typing import Optional

import click

from mynd.backend import metashape
from mynd.collections import CameraGroup
from mynd.image import ImageType

from mynd.tasks.export_cameras import export_camera_group

from mynd.utils.filesystem import (
    list_directory,
    create_resource,
    Resource,
    ResourceManager,
)

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


GroupID = CameraGroup.Identifier
Resources = list[Resource]


IMAGE_FILE_PATTERN: str = "*.tiff"


@click.group()
@click.pass_context
def camera_cli(context: click.Context) -> None:
    """CLI for camera specific tasks."""
    context.ensure_object(dict)


@camera_cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("destination", type=click.Path())
@click.argument("target", type=str)
@click.option("--colors", type=str)
@click.option("--ranges", type=str)
@click.option("--normals", type=str)
def export_cameras(
    source: str,
    destination: str,
    target: str,
    colors: Optional[str],
    ranges: Optional[str],
    normals: Optional[str],
) -> None:
    """Exports camera data from the backend.

    :arg source:            backend project source
    :arg destination:       export destination
    :arg target:            target group label
    :arg colors:            album of color images
    :arg ranges:            album of range images
    :arg normals:           album of normal images
    """

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
    # NOTE: Add option to export images (range and normal maps)

    cameras: CameraGroup = retrieve_camera_group(target).unwrap()
    images: dict[ImageType, Resources] = retrieve_images(image_sources).unwrap()

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


def retrieve_images(image_sources: Mapping[ImageType, str | Path]) -> Result:
    """Retrieve images from sources."""

    image_tags: dict[ImageType, list[str]] = {
        image_type: ["image", str(image_type)] for image_type in image_sources
    }

    manager: ResourceManager = collect_image_resources(image_sources, image_tags)

    image_groups: dict[ImageType, Resources] = {
        image_type: manager.query_tags(tags)
        for image_type, tags in image_tags.items()
    }

    return image_groups


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
