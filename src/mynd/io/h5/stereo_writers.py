"""Module for I/O for camera data."""

from collections.abc import Callable
from typing import Any, NamedTuple

from mynd.camera import CameraCalibration
from mynd.geometry import (
    PixelMap,
    StereoRectificationTransforms,
    StereoRectificationResult,
)
from mynd.utils.result import Ok

from .database import H5Database
from .sensor_writers import insert_calibration_into


Group = H5Database.Group
DataWriter = Callable[[Group, Any], None]


class WriteComponent(NamedTuple):
    """Class representing a write item."""

    group_name: str
    data: Any
    write_fun: DataWriter


def insert_stereo_rectification_into(
    group: Group, rectification: StereoRectificationResult
) -> None:
    """Writes a rectification result to a file database group."""

    write_components: list[WriteComponent] = [
        WriteComponent(
            "calibrations/distorted/first",
            rectification.calibrations.first,
            insert_calibration_into,
        ),
        WriteComponent(
            "calibrations/distorted/second",
            rectification.calibrations.first,
            insert_calibration_into,
        ),
        WriteComponent(
            "calibrations/undistorted/first",
            rectification.rectified_calibrations.first,
            insert_calibration_into,
        ),
        WriteComponent(
            "calibrations/undistorted/second",
            rectification.rectified_calibrations.second,
            insert_calibration_into,
        ),
        WriteComponent(
            "pixel_maps/forward/first",
            rectification.pixel_maps.first,
            _write_pixel_map,
        ),
        WriteComponent(
            "pixel_maps/forward/second",
            rectification.pixel_maps.second,
            _write_pixel_map,
        ),
        WriteComponent(
            "pixel_maps/inverse/first",
            rectification.inverse_pixel_maps.first,
            _write_pixel_map,
        ),
        WriteComponent(
            "pixel_maps/inverse/second",
            rectification.inverse_pixel_maps.second,
            _write_pixel_map,
        ),
        WriteComponent(
            "transforms",
            rectification.transforms,
            _write_rectification_transforms,
        ),
    ]

    for component in write_components:
        subgroup: Group = group.create_group(component.group_name)
        component.write_fun(subgroup, component.data)

    return Ok(None)


def _write_pixel_map(group: Group, pixel_map: PixelMap) -> None:
    """Adds a pixel map to a database group."""

    group.attrs["type"] = "pixel_map"
    group.attrs["description"] = GROUP_DESCRIPTIONS.get(PixelMap)
    group.create_dataset("mapping", data=pixel_map.to_array())


def _write_rectification_transforms(
    group: Group, transforms: StereoRectificationTransforms
) -> None:
    """Adds rectification transforms to a file database group."""

    group.attrs["type"] = "rectification_transforms"
    group.attrs["description"] = GROUP_DESCRIPTIONS.get(
        StereoRectificationTransforms
    )

    group.create_dataset("common_rotation", data=transforms.rotation)
    group.create_dataset("homography/first", data=transforms.homographies.first)
    group.create_dataset(
        "homography/second", data=transforms.homographies.second
    )


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
    StereoRectificationTransforms: TRANSFORM_DESCRIPTION,
}
