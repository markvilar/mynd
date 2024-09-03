"""Module for geometry helper functionality."""

import Metashape

import numpy as np

from ...camera import CameraCalibration, Image, ImageFormat
from ...geometry import compute_normals_from_range

from .camera_helpers import compute_camera_calibration
from .image_helpers import convert_image


def render_range_and_normal_maps(camera: Metashape.Camera) -> tuple[Image, Image]:
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
    range_map.format = ImageFormat.X

    normals: np.ndarray = compute_normals_from_range(
        range_map.data,
        camera_matrix=calibration.camera_matrix,
        flipped=True,
    )

    normal_map: Image = Image(data=normals, format=ImageFormat.XYZ)

    return range_map, normal_map
