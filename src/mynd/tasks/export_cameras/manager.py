"""Module for managing export of camera attributes, metadata, and images."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypeVar

from mynd.camera import Camera, Metadata
from mynd.collections import CameraGroup
from mynd.image import (
    Image,
    ImageType,
    ImageComposite,
    ImageCompositeLoader,
)
from mynd.io import read_image
from mynd.io.h5 import H5Database, create_file_database, load_file_database

from mynd.utils.composition import create_composite_builder
from mynd.utils.filesystem import (
    list_directory,
    create_resource,
    create_resource_matcher,
    Resource,
    ResourceManager,
)
from mynd.utils.log import logger
from mynd.utils.result import Ok, Result

# Import handlers for subtasks
from .camera_handler import handle_camera_export
from .image_handler import handle_image_export


CameraID = Camera.Identifier


T: TypeVar = TypeVar("T")


ErrorType = str
ResultType = Result[T, ErrorType]


METADATA_STORAGE_GROUP: str = "metadata"
IMAGE_STORAGE_GROUP: str = "images"
IMAGE_FILE_PATTERN: str = "*.tiff"


@dataclass
class CameraExportData:
    """Class representing camera export data."""

    name: str
    storage: H5Database.Group
    cameras: CameraGroup
    image_loaders: dict[str, ImageCompositeLoader]
    metadata: dict[CameraID, Metadata]


def manage_camera_group_export(
    destination: Path,
    cameras: CameraGroup,
    images: Optional[Mapping[ImageType, str | Path]] = None,
    metadata: Optional[Mapping[CameraID, Metadata]] = None,
) -> ResultType[None]:
    """Entrypoint for exporting camera groups. Initializes data storage and
    dispatches to relevant subtasks.

    :arg destination:   export destination (file)
    :arg cameras:       group of camera data (attributes, references)
    :arg images:        image directories or filesystem search patterns
    :arg metadata:      camera metadata
    """

    _storage: H5Database.Group = prepare_data_storage(
        destination, name=cameras.identifier.label
    )

    if images:
        loaders: list[ImageCompositeLoader] = prepare_image_loaders(images)
    else:
        loaders = None

    # TODO: Match images and create loaders

    export_data: CameraExportData = CameraExportData(
        destination,
        cameras.identifier.label,
        cameras,
        loaders,
        metadata,
    )

    log_task_header(export_data)

    # Export camera attributes and references
    handle_camera_export(
        export_data.storage, export_data.cameras, error_callback=on_error
    )

    # In order to export images, we check that an image storage group is not
    # already present in the database, and that bundle loaders are provided
    if IMAGE_STORAGE_GROUP in export_data.storage:
        logger.warning(
            f"'{IMAGE_STORAGE_GROUP}' is already in storage group {export_data.storage.name}"
        )
        pass
    elif export_data.images:
        handle_image_export(
            export_data.storage.base,
            export_data.cameras.attributes,
            export_data.images,
            error_callback=on_error,
        )

    return Ok(None)


def prepare_data_storage(destination: Path, name: str) -> H5Database.Group:
    """Prepare storage group."""

    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    if name in database:
        storage_group: H5Database.Group = database.get(name)
    else:
        storage_group: H5Database.Group = database.create_group(name).unwrap()

    return storage_group


Resources = list[Resource]
ComponentSources = Mapping[ImageType, Resource]


def prepare_image_loaders(
    sources: dict[ImageType, str | Path]
) -> dict[str, ImageCompositeLoader]:
    """Prepares image loaders by collecting image resources, matching them, and
    building loaders."""

    image_tags: dict[ImageType, list[str]] = {
        image_type: ["image", str(image_type)] for image_type in sources
    }

    manager: ResourceManager = collect_image_resources(sources, image_tags)

    image_groups: dict[ImageType, Resources] = {
        image_type: manager.query_tags(tags)
        for image_type, tags in image_tags.items()
    }

    matcher = create_resource_matcher()
    component_sources: list[ComponentSources] = matcher(image_groups)

    builder = create_composite_builder(
        loader_factory=create_image_composite_loader,
        labeller=label_image_composite,
    )
    loaders: dict[str, ImageCompositeLoader] = builder(component_sources)

    return loaders


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
        resources: list[Resource] = [
            create_resource(path) for path in files if path.exists()
        ]

        if len(resources) == 0:
            logger.warning(f"no resources for type: {image_type}")

        image_manager.add_resources(resources, tags=tags.get(image_type))

    return image_manager


# NOTE: Defines how components are loaded
def create_image_composite_loader(
    components: dict[ImageType, Resource]
) -> ImageCompositeLoader:
    """Creates an image composite loader from component sources."""

    def load_image_composite() -> ImageComposite:
        """Loads an image composite from resources."""
        image_components: dict[ImageType, Image] = {
            image_type: read_image(resource.handle).unwrap()
            for image_type, resource in components.items()
        }
        return ImageComposite(image_components)

    return load_image_composite


# NOTE: Defines how components are labelled
def label_image_composite(components: Mapping[ImageType, Resource]) -> str:
    """Labels a collection of image components."""
    if ImageType.COLOR in components:
        label: str = components.get(ImageType.COLOR).stem
    else:
        label: str = [components.values()][0].stem
    return label


def log_task_header(export_data: CameraExportData) -> None:
    """Logs a header with summary statistics before exporting cameras."""

    if export_data.images is not None:
        image_count: int = sum(
            [len(items) for items in export_data.images.values()]
        )
    else:
        image_count: int = 0

    cameras: CameraGroup = export_data.cameras

    group_label: str = cameras.identifier.label
    camera_count: int = len(cameras.attributes.identifiers)
    estimated_count: int = len(cameras.estimated_references.identifiers)
    prior_count: int = len(cameras.prior_references.identifiers)

    logger.info("")
    logger.info(f"Exporting camera group: {group_label}")
    logger.info(f"Camera attributes:      {camera_count}")
    logger.info(f"Estimated references:   {estimated_count}")
    logger.info(f"Prior references:       {prior_count}")
    logger.info(f"Images:                 {image_count}")
    logger.info("")


def on_error(message: str) -> None:
    """Callback that is called on an error result."""
    logger.error(message)
