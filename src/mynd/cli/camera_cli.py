"""Module for camera related CLI functionality."""

from pathlib import Path
from typing import Optional

import click

from ..api import GroupID, CameraAttributeGroup, CameraReferenceGroup
from ..backend import metashape
from ..camera import ImageBundleLoader

from ..tasks.export_cameras import export_camera_group
from ..tasks.export_images import generate_image_bundle_loaders

from ..utils.log import logger
from ..utils.result import Ok, Err, Result


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
@click.option("--images", type=click.Path(exists=True))
@click.option("--ranges", type=click.Path(exists=True))
@click.option("--normals", type=click.Path(exists=True))
def export_cameras(
    source: str,
    destination: str,
    target: str,
    stereo: bool,
    images: Optional[click.Path],
    ranges: Optional[click.Path],
    normals: Optional[click.Path],
) -> None:
    """Exports camera data from the backend."""

    # TODO: Validate arguments
    source: Path = Path(source)
    destination: Path = Path(destination)

    assert source.exists(), f"source {source} does not exist"
    assert destination.parent.exists(), f"destination {destination} does not exist"

    # TODO: Prepare camera export

    metashape.load_project(source).unwrap()
    url: str = metashape.get_project_url().unwrap()

    logger.info(f"Project: {url}")

    group_identifiers: list[GroupID] = metashape.get_group_identifiers().unwrap()
    target_group: Optional[GroupID] = get_target_group(target, group_identifiers)

    if target_group is None:
        group_labels: list[str] = [identifier.label for identifier in group_identifiers]
        logger.error(f"could not find target group: {target}")
        logger.error(f"groups in project are: {*group_labels,}")
        return

    # Get camera data from backend
    attribute_groups: dict[GroupID, CameraAttributeGroup] = (
        metashape.get_camera_attributes().unwrap()
    )
    estimated_reference_groups: dict[GroupID, CameraReferenceGroup] = (
        metashape.get_estimated_camera_references().unwrap()
    )
    prior_reference_groups: dict[GroupID, CameraReferenceGroup] = (
        metashape.get_prior_camera_references().unwrap()
    )

    attributes: CameraAttributeGroup = attribute_groups.get(target_group)
    estimated_references: CameraReferenceGroup = estimated_reference_groups.get(target_group)
    prior_references: CameraReferenceGroup = prior_reference_groups.get(target_group)

    # Generate image bundle loaders
    if images is not None and ranges is not None and normals is not None:
        bundle_loaders: dict[str, ImageBundleLoader] = generate_image_bundle_loaders(
            Path(images), Path(ranges), Path(normals), pattern="*.tiff"
        )
    else:
        bundle_loaders = None

    # NOTE: Basic export setup is to export basic camera data (references, attributes, sensors)
    # NOTE: Add option to export stereo calibrations
    # NOTE: Add option to export images (range and normal maps)

    export_result: Result[str, str] = export_camera_group(
        destination,
        target_group,
        attributes,
        estimated_references,
        prior_references,
        bundle_loaders,
    )


def get_target_group(target: str, identifiers: list[GroupID]) -> Optional[GroupID]:
    """Returns a group identifier if it matches the target label, and none otherwise."""

    matches: list[GroupID] = [
        identifier for identifier in identifiers if identifier.label == target
    ]

    if not matches:
        return None

    return matches[0]
