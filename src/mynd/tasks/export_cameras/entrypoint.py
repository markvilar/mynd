"""Module for managing export of camera attributes, metadata, and images."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypeVar, TypeAlias

from mynd.camera import CameraID, SensorID
from mynd.collections import CameraGroup, SensorImages
from mynd.image import (
    Image,
    ImageType,
    ImageComposite,
    ImageCompositeLoader,
)

from mynd.io import read_image

from mynd.utils.composition import create_composite_builder
from mynd.utils.filesystem import create_resource_matcher, Resource
from mynd.utils.log import logger
from mynd.utils.result import Result

# Import handlers for subtasks
from .export_database import export_cameras_database
from .export_data_frame import export_cameras_data_frame


Resources: TypeAlias = list[Resource]
ImageResourceGroups: TypeAlias = Mapping[ImageType, Resources]


T: TypeVar = TypeVar("T")


ErrorType = str
ResultType = Result[T, ErrorType]


@dataclass
class ExportData:
    """Class representing export data."""

    cameras: CameraGroup
    image_groups: Optional[list[SensorImages]] = None

    def has_images(self) -> bool:
        """Returns true if the export data contains images."""
        return self.image_groups is not None


def export_camera_group(
    destination: Path,
    cameras: CameraGroup,
    images: Optional[ImageResourceGroups] = None,
) -> ResultType[None]:
    """Entrypoint for exporting camera groups. Prepares export data,
    and dispatches to the relevant subtasks.

    :arg destination:   export destination path
    :arg cameras:       group of camera data (attributes, references)
    :arg images:        image resource groups
    :arg metadata:      camera metadata
    """

    # TODO: Create task context?

    export_data: ExportData = prepare_export_data(cameras, images)

    log_task_header(export_data)

    match destination.suffix:
        case ".h5" | ".hdf5":
            export_cameras_database(destination, export_data.cameras, export_data.image_groups)
        case ".csv":
            export_cameras_data_frame(destination, export_data.cameras)
        case _:
            raise NotImplementedError


def prepare_export_data(
    cameras: CameraGroup,
    images: Optional[ImageResourceGroups] = None,
) -> ExportData:
    """Prepares export data by preparing cameras, images, and metadata."""

    export_data: ExportData = ExportData(cameras)

    if images:
        export_data.image_groups = prepare_sensor_images(cameras, images)

    return export_data


ComponentSources = Mapping[ImageType, Resource]


def prepare_sensor_images(
    cameras: CameraGroup,
    images: Mapping[ImageType, Resources],
) -> list[SensorImages]:
    """Prepare images by matching image components, and creating and
    labelling loaders. Image loaders are also grouped by camera sensor."""

    matcher = create_resource_matcher()
    component_sources: list[ComponentSources] = matcher(images)

    builder = create_composite_builder(
        factory=create_image_composite_loader,
        labeller=label_image_composite,
    )
    loaders: dict[str, ImageCompositeLoader] = builder(component_sources)

    image_groups: list[SensorImages] = group_images_by_sensor(
        cameras.attributes,
        loaders,
    )

    return image_groups


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
        label: str = list(components.values())[0].stem
    return label


def group_images_by_sensor(
    attributes: CameraGroup.Attributes,
    image_loaders: dict[str, ImageCompositeLoader],
) -> list[SensorImages]:
    """Group image loaders based on the sensors that captured them."""

    image_loaders: dict[CameraID, ImageCompositeLoader] = {
        identifier: image_loaders.get(identifier.label)
        for identifier in attributes.identifiers
        if identifier.label in image_loaders
    }

    sensor_loaders: dict[SensorID, dict[CameraID, ImageCompositeLoader]] = (
        dict()
    )
    for sensor, cameras in attributes.sensor_cameras.items():
        sensor_loaders[sensor] = {
            camera: image_loaders.get(camera)
            for camera in cameras
            if camera in image_loaders
        }

    image_groups: list[SensorImages] = [
        SensorImages(sensor, loaders)
        for sensor, loaders in sensor_loaders.items()
    ]

    return image_groups


def log_task_header(export_data: ExportData) -> None:
    """Logs a header with summary statistics before exporting cameras."""

    if export_data.image_groups is not None:
        image_count: int = sum(
            [len(group.loaders) for group in export_data.image_groups]
        )
    else:
        image_count: int = 0

    cameras: CameraGroup = export_data.cameras

    group_label: str = cameras.group_identifier.label
    camera_count: int = len(cameras.attributes.identifiers)
    estimated_count: int = len(cameras.reference_estimates.identifiers)
    prior_count: int = len(cameras.reference_priors.identifiers)

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
