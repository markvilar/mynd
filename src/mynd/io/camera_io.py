"""Module for I/O for camera data."""

from collections.abc import Callable
from typing import Any, NamedTuple

from ..camera import CameraCalibration
from ..geometry import PixelMap, RectificationTransforms, RectificationResult
from ..utils.result import Ok, Err, Result

from .file_database import H5Database


def write_rectification_results_to_file_database(
    database: H5Database,
    group_name: str,
    rectification: RectificationResult,
) -> Result[None, str]:
    """Adds rectification results to a file database group."""

    # Create database group and add rectification results to it
    if group_name in database:
        return Err(f"file database already contains group: {group_name}")

    group = database.create_group(group_name)

    if not group:
        return Err(f"could not create group: {group_name}")

    # TODO: Add return type
    _write_rectification_data_to_group(group, rectification)

    return Ok(None)


Group = H5Database.Group
DataWriter = Callable[[Group, Any], None]


class WriteTask(NamedTuple):
    """Class representing a write item."""

    group_name: str
    data: Any
    write_fun: DataWriter


def _write_rectification_data_to_group(
    group: Group, rectification: RectificationResult
) -> None:
    """Writes a rectification result to a file database group."""

    write_tasks: list[WriteTask] = [
        WriteTask(
            "calibrations/raw/first",
            rectification.calibrations.first,
            _write_camera_calibration,
        ),
        WriteTask(
            "calibrations/raw/second",
            rectification.calibrations.first,
            _write_camera_calibration,
        ),
        WriteTask(
            "calibrations/rectified/first",
            rectification.rectified_calibrations.first,
            _write_camera_calibration,
        ),
        WriteTask(
            "calibrations/rectified/second",
            rectification.rectified_calibrations.second,
            _write_camera_calibration,
        ),
        WriteTask(
            "pixel_maps/forward/first", rectification.pixel_maps.first, _write_pixel_map
        ),
        WriteTask(
            "pixel_maps/forward/second",
            rectification.pixel_maps.second,
            _write_pixel_map,
        ),
        WriteTask(
            "pixel_maps/inverse/first",
            rectification.inverse_pixel_maps.first,
            _write_pixel_map,
        ),
        WriteTask(
            "pixel_maps/inverse/second",
            rectification.inverse_pixel_maps.second,
            _write_pixel_map,
        ),
        WriteTask(
            "transforms", rectification.transforms, _write_rectification_transforms
        ),
    ]

    for task in write_tasks:
        subgroup: Group = group.create_group(task.group_name)
        task.write_fun(subgroup, task.data)


def _write_camera_calibration(group: Group, calibration: CameraCalibration) -> None:
    """Adds a camera calibration to a file database group."""

    group.attrs["type"] = "calibration"
    group.attrs["description"] = GROUP_DESCRIPTIONS.get(CameraCalibration)

    group.create_dataset("width", data=calibration.width, shape=(1,))
    group.create_dataset("height", data=calibration.height, shape=(1,))
    group.create_dataset("camera_matrix", data=calibration.camera_matrix)
    group.create_dataset("distortion", data=calibration.distortion)
    group.create_dataset("location", data=calibration.location)
    group.create_dataset("rotation", data=calibration.rotation)


def _write_pixel_map(group: Group, pixel_map: PixelMap) -> None:
    """Adds a pixel map to a database group."""

    group.attrs["type"] = "pixel_map"
    group.attrs["description"] = GROUP_DESCRIPTIONS.get(PixelMap)

    group.create_dataset("width", data=pixel_map.width, shape=(1,))
    group.create_dataset("height", data=pixel_map.height, shape=(1,))
    group.create_dataset("mapping", data=pixel_map.to_array())


def _write_rectification_transforms(
    group: Group, transforms: RectificationTransforms
) -> None:
    """Adds rectification transforms to a file database group."""

    group.attrs["type"] = "rectification_transforms"
    group.attrs["description"] = GROUP_DESCRIPTIONS.get(RectificationTransforms)

    group.create_dataset("common_rotation", data=transforms.rotation)
    group.create_dataset("homography/first", data=transforms.homographies.first)
    group.create_dataset("homography/second", data=transforms.homographies.second)


CALIBRATION_DESCRIPTION: str = """This group contains a camera calibration with the 
following components:
- camera matrix
- distortion coefficients
- image width and heigth
- reference location
- reference rotation

The distortion coeff. are defined according to OpenCV: [k1, k2, p1, p2, k3]
Where k1, k2, k3 are coefficients for radial distort, and p1 and p2 for tangential."""


PIXEL_MAP_DESCRIPTION: str = """This group contains a pixel map that geometrically 
changes the pixels of an image. The pixel map has a shape of HxWx2 and can be used 
directly in OpenCVs remap function."""


TRANSFORM_DESCRIPTION: str = """This group contains camera transforms for rectifying 
a pair of rigidly mounted cameras. The transforms include rectifying homographies for 
the first and second camera, and a common rotation in object space."""


GROUP_DESCRIPTIONS: dict[type, str] = {
    CameraCalibration: CALIBRATION_DESCRIPTION,
    PixelMap: PIXEL_MAP_DESCRIPTION,
    RectificationTransforms: TRANSFORM_DESCRIPTION,
}
