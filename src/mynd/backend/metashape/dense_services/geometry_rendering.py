"""Module for geometry helper functionality."""

import Metashape

import numpy as np

from mynd.camera import CameraCalibration
from mynd.image import Image, PixelFormat
from mynd.geometry import compute_normals_from_range

from ..helpers.camera import compute_camera_calibration
from ..helpers.image import convert_image


def render_range_and_normal_maps(
    camera: Metashape.Camera,
) -> tuple[Image, Image]:
    """Render range and normal map for a Metashape camera."""

    if camera.chunk.transform.scale:
        scale: float = camera.chunk.transform.scale
    else:
        scale: float = 1.0

    range_map: Metashape.Image = camera.chunk.model.renderDepth(
        camera.transform, camera.sensor.calibration, add_alpha=False
    )

    range_map: Metashape.Image = scale * range_map
    range_map: Metashape.Image = range_map.convert(" ", "F32")

    # Compute a camera calibration and range array to calculate the normal map
    calibration: CameraCalibration = compute_camera_calibration(
        camera.sensor.calibration
    )
    range_map: Image = convert_image(range_map)
    range_map.format = PixelFormat.X

    normals: np.ndarray = compute_normals_from_range(
        range_map.data,
        camera_matrix=calibration.camera_matrix,
        flipped=True,
    )

    normal_map: Image = Image.from_array(data=normals, format=PixelFormat.XYZ)

    return range_map, normal_map
