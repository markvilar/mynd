"""Module for managing export of camera attributes, metadata, and images."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, TypeAlias

from mynd.camera import CameraID, Metadata, SensorID
from mynd.collections import CameraGroup, SensorImages
from mynd.image import (
    Image,
    ImageType,
    ImageComposite,
    ImageCompositeLoader,
)

from mynd.io import read_image
from mynd.io.h5 import H5Database, create_file_database, load_file_database

from mynd.utils.composition import create_composite_builder
from mynd.utils.filesystem import create_resource_matcher, Resource
from mynd.utils.log import logger
from mynd.utils.result import Result

# Import handlers for subtasks
from .export_handlers import (
    handle_camera_export,
    handle_image_export,
    handle_metadata_export,
)


T: TypeVar = TypeVar("T")

Resources: TypeAlias = list[Resource]
ImageResourceGroups: TypeAlias = Mapping[ImageType, Resources]
CameraMetadata: TypeAlias = Mapping[CameraID, Metadata]

ErrorType = str
ResultType = Result[T, ErrorType]


CAMERA_STORAGE_NAME: str = "cameras"
IMAGE_STORAGE_GROUP: str = "images"
METADATA_STORAGE_GROUP: str = "metadata"


H5Group: TypeAlias = H5Database.Group


@dataclass
class ExportData:
    """Class representing export data."""

    cameras: CameraGroup
    image_groups: Optional[list[SensorImages]] = None
    metadata: Optional[CameraMetadata] = None


@dataclass
class ExportConfig:
    """Class representing an export task."""

    arguments: dict[str, Any]
    storage: H5Group
    handler: Callable
    result_callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None


def export_camera_group(
    destination: Path,
    cameras: CameraGroup,
    images: Optional[ImageResourceGroups] = None,
    metadata: Optional[CameraMetadata] = None,
) -> ResultType[None]:
    """Entrypoint for exporting camera groups. Prepare export data,
    initializes data storage, and dispatches to the relevant subtasks.

    :arg destination:   export destination path
    :arg cameras:       group of camera data (attributes, references)
    :arg images:        image resource groups
    :arg metadata:      camera metadata
    """

    export_data: ExportData = prepare_export_data(cameras, images)
    export_tasks: list[ExportConfig] = create_export_configs(destination, export_data)

    log_task_header(export_data)

    for task in export_tasks:
        task.handler(
            storage=task.storage,
            **task.arguments,
            result_callback=task.result_callback,
            error_callback=task.error_callback,
        )


def prepare_export_data(
    cameras: CameraGroup,
    images: Optional[ImageResourceGroups] = None,
    metadata: Optional[CameraMetadata] = None,
) -> ExportData:
    """Prepares export data by preparing cameras, images, and metadata."""

    export_data: ExportData = ExportData(cameras)
    
    if images:
        export_data.image_groups = prepare_sensor_images(cameras, images)

    if metadata:
        export_data.metadata = metadata

    return export_data


def create_export_configs(destination: Path, export_data: ExportData) -> None:
    """Creates export configurations by loading a database and creating storage groups."""

    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    base_name: str = export_data.cameras.identifier.label

    # Create the base group
    base_group: H5Group = database.create_group(base_name).unwrap()

    export_configs: list[ExportConfig] = list()
    
    # TODO: Configure subtask for cameras
    export_configs.append(
        configure_camera_export(base_group, CAMERA_STORAGE_NAME, export_data.cameras)
    )
    
    # TODO: Configure subtasks for image groups
    if export_data.image_groups is not None:
        for image_group in export_data.image_groups:
            
            storage_name: str = f"{IMAGE_STORAGE_GROUP}/{image_group.sensor.identifier.label}"
            
            export_configs.append(
                configure_image_export(
                    base=base_group,
                    storage_name=storage_name,
                    images=image_group,
                )
            )

    # TODO: Configure subtasks for metadata
    if export_data.metadata is not None:
        export_configs.append(
            configure_metadata_export(
                base=base_group, 
                storage_name=METADATA_STORAGE_GROUP,
                metadata=export_data.metadata,
            )
        )
    
    return export_configs


def configure_camera_export(
    base: H5Group, 
    storage_name: str, 
    cameras: CameraGroup,
) -> ExportConfig:
    """Creates a camera export configuration."""
    storage_group: H5Group = base.create_group(storage_name).unwrap()
    return ExportConfig(
        arguments={"cameras": cameras},
        storage=storage_group,
        handler=handle_camera_export,
    )


def configure_image_export(
    base: H5Group, 
    storage_name: str, 
    images: SensorImages
) -> ExportConfig:
    """Creates an image export configuration."""
    storage_group: H5Group = base.create_group(storage_name).unwrap()
    return ExportConfig(
        arguments={"images": images},
        storage=storage_group,
        handler=handle_image_export,
    )


def configure_metadata_export(
    base: H5Group, 
    storage_name: str, 
    metadata: CameraMetadata,
) -> ExportConfig:
    """Creates a metadata export configuration."""
    storage_group: H5Group = base.create_group(storage_name).unwrap()
    return ExportConfig(
        arguments={"metadata": metadata},
        storage=storage_group,
        handler=handle_metadata_export,
    )


ComponentSources = Mapping[ImageType, Resource]


def prepare_sensor_images(
    cameras: CameraGroup, 
    images: Mapping[ImageType, Resources],
) -> list[SensorImages]:
    """TODO"""
    
    matcher = create_resource_matcher()
    component_sources: list[ComponentSources] = matcher(images)

    builder = create_composite_builder(
        loader_factory=create_image_composite_loader,
        labeller=label_image_composite,
    )
    loaders: dict[str, ImageCompositeLoader] = builder(component_sources)    
    
    sensor_images: list[SensorImages] = group_images_by_sensor(
        cameras.attributes,
        loaders,
    )

    return sensor_images


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


def label_image_composite(components: Mapping[ImageType, Resource]) -> str:
    """Labels a collection of image components."""
    if ImageType.COLOR in components:
        label: str = components.get(ImageType.COLOR).stem
    else:
        label: str = [components.values()][0].stem
    return label


def group_images_by_sensor(
    attributes: CameraGroup.Attributes, 
    image_loaders: dict[str, ImageCompositeLoader]
) -> list[SensorImages]:
    """Group image loaders based on the sensors that captured them."""

    image_loaders: dict[CameraID, ImageCompositeLoader] = {
        identifier: image_loaders.get(identifier.label) for identifier in attributes.identifiers
        if identifier.label in image_loaders
    }

    sensor_loaders: dict[SensorID, dict[CameraID, ImageCompositeLoader]] = dict()
    for sensor, cameras in attributes.sensor_cameras:
        sensor_loaders[sensor] = {
            camera: image_loaders.get(camera) for camera in cameras if camera.label in image_loaders
        }


    image_groups: list[SensorImages] = [
        SensorImages(sensor, loaders) for sensor, loaders in sensor_loaders.items()
    ]

    return image_groups


def log_task_header(export_data: ExportData) -> None:
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
