"""Module for exporting camera data including keys, labels, images, and references."""

from pathlib import Path
from typing import Optional

from ..api import GroupID, CameraAttributeGroup, CameraReferenceGroup
from ..camera import ImageBundleLoader
from ..database import H5Database, create_file_database, load_file_database
from ..utils.log import logger
from ..utils.result import Result


ImageBundleLoaders = dict[str, ImageBundleLoader]


def export_camera_group(
    destination: str | Path,
    identifier: GroupID,
    camera_attributes: CameraAttributeGroup,
    estimated_references: CameraReferenceGroup,
    prior_references: CameraReferenceGroup,
    bundle_loaders: Optional[ImageBundleLoaders],
) -> Result[str, str]:
    """Exports camera data to a given destination."""

    destination: Path = Path(destination)

    if destination.exists():
        database: H5Database = load_file_database(destination).unwrap()
    else:
        database: H5Database = create_file_database(destination).unwrap()

    bundle_count: int = len(bundle_loaders) if bundle_loaders else 0

    logger.info(f"Exporting camera group: {identifier.label}")
    logger.info(f"  Camera attributes:      {len(camera_attributes.keys)}")
    logger.info(f"  Estimated references:   {len(estimated_references.keys)}")
    logger.info(f"  Prior references:       {len(prior_references.keys)}")
    logger.info(f"  Image bundles:          {bundle_count}")

    # TODO: Create root group
    if identifier.label in database:
        root_group: H5Database.Group = database.get(identifier.label)
    else:
        root_group: H5Database.Group = database.create_group(identifier.label)


    # TODO: Group images by sensor and add camera keys
    make_sensor_to_image_mapping(camera_attributes)

    raise NotImplementedError("export_camera_data is not implemented")


def make_sensor_to_image_mapping(attributes: CameraAttributeGroup) -> None:
    """TODO"""
    image_map: dict[int, str] = attributes.image_labels
    sensor_map: dict[int, int] = attributes.sensor_keys

    sensor_to_camera: dict[int, int] = dict()
    for camera, sensor in attributes.sensor_keys.items():
        pass

    raise NotImplementedError("make_sensor_to_image_mapping is not implemented")
