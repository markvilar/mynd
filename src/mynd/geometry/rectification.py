"""Module for stereo camera rectification."""

from dataclasses import dataclass
from typing import NamedTuple, Optional

import cv2
import numpy as np

from ..camera import CameraCalibration, Image
from ..containers import Pair

from .image_transformations import (
    PixelMap,
    compute_pixel_map,
    remap_image_pixels,
    invert_pixel_map,
)
from .image_transformations import ImageCorners, get_image_corners


class StereoRectificationTransforms(NamedTuple):
    """Class representing rectification transforms including
    a common rotation and homographies for the two cameras."""

    rotation: np.ndarray  # common rotation for the two cameras
    homographies: Pair[np.ndarray]  # transforms for the two camera


def compute_rectifying_camera_transforms(
    calibrations: Pair[CameraCalibration],
) -> StereoRectificationTransforms:
    """
    Compute the rectifying transforms for a pair of sensors using the standard OpenCV algorithm.
    Adopted from: https://github.com/decadenza/SimpleStereo/blob/master/simplestereo/_rigs.py
    """

    resolution: tuple[int, int] = (calibrations.first.width, calibrations.first.height)

    first_rotation, second_rotation, _, _, _, _, _ = cv2.stereoRectify(
        calibrations.first.camera_matrix,  # 3x3 master camera matrix
        calibrations.first.distortion,  # 5x1 master camera distortion
        calibrations.second.camera_matrix,  # 3x3 slave camera matrix
        calibrations.second.distortion,  # 5x1 slave camera distortion
        resolution,  # resolution (width, height)
        calibrations.second.rotation,  # 3x3 rotation matrix from master to slave
        calibrations.second.location,  # 3x1 translation vector from master to slave
        flags=0,
    )

    # OpenCV does not compute the rectifying homography, but a rotation in the object space.
    # R1 = Rnew * Rcam^{-1}
    # To get the homography:
    first_homography: np.ndarray = first_rotation.dot(
        np.linalg.inv(calibrations.first.camera_matrix)
    )
    second_homography: np.ndarray = second_rotation.dot(
        np.linalg.inv(calibrations.second.camera_matrix)
    )

    homographies: Pair[np.ndarray] = Pair(
        first=first_homography, second=second_homography
    )

    # To get the common orientation, since the first camera has orientation as origin:
    # Rcommon = R1
    # It also can be retrieved from R2, cancelling the rotation of the second camera.
    # Rcommon = R2.dot(np.linalg.inv(rig.R))

    return StereoRectificationTransforms(
        rotation=first_rotation, homographies=homographies
    )


@dataclass
class StereoRectificationResult:
    """Class representing a rectification results, including original camera calibrations,
    rectified camera calibrations, pixel maps, inverse pixel maps, and rectifying transforms.
    """

    calibrations: Pair[CameraCalibration]
    rectified_calibrations: Pair[CameraCalibration]
    pixel_maps: Pair[PixelMap]
    inverse_pixel_maps: Pair[PixelMap]
    transforms: StereoRectificationTransforms


def compute_rectifying_image_transforms(
    calibrations: Pair[CameraCalibration],
    transforms: StereoRectificationTransforms,
) -> StereoRectificationResult:
    """Computes updated camera matrices and pixel maps based on the given stereo calibration
    and rectifying transforms."""

    # Update camera calibrations for the images after applying pixel map.
    # Since the pixel maps undistort the images, the distortion coefficients are zeros.
    updated_calibrations: Pair[CameraCalibration] = _compute_rectified_calibrations(
        calibrations,
        transforms,
    )

    # Recompute final maps considering fitting transformations too
    pixel_maps: Pair[PixelMap] = Pair(
        first=compute_pixel_map(
            calibrations.first.camera_matrix,
            calibrations.first.distortion,
            updated_calibrations.first.rotation,
            updated_calibrations.first.camera_matrix,
            (updated_calibrations.first.width, updated_calibrations.first.height),
        ),
        second=compute_pixel_map(
            calibrations.second.camera_matrix,
            calibrations.second.distortion,
            updated_calibrations.second.rotation,
            updated_calibrations.second.camera_matrix,
            (updated_calibrations.second.width, updated_calibrations.second.height),
        ),
    )

    # Compute inverse pixel maps to ease transforming between rectified and unrectified
    inverse_pixel_maps: Pair[PixelMap] = Pair(
        first=invert_pixel_map(pixel_maps.first),
        second=invert_pixel_map(pixel_maps.second),
    )

    result: StereoRectificationResult = StereoRectificationResult(
        calibrations=calibrations,
        rectified_calibrations=updated_calibrations,
        pixel_maps=pixel_maps,
        inverse_pixel_maps=inverse_pixel_maps,
        transforms=transforms,
    )

    return result


def _compute_rectified_calibrations(
    calibrations: Pair[CameraCalibration],
    transforms: StereoRectificationTransforms,
) -> Pair[CameraCalibration]:
    """Computes the camera calibrations for a pair of rectified cameras."""

    resolution_master: tuple[int, int] = (
        calibrations.first.width,
        calibrations.first.height,
    )
    resolution_slave: tuple[int, int] = (
        calibrations.second.width,
        calibrations.second.height,
    )

    desired_resolution: tuple[int, int] = resolution_master

    affine_transform: np.ndarray = _compute_common_affine_transform(
        calibrations.first.camera_matrix,  # intrinsic 1
        calibrations.second.camera_matrix,  # intrinsic 2
        transforms.homographies.first,  # homography 1
        transforms.homographies.second,  # homography 2
        resolution_master,  # resolution 1
        resolution_slave,  # resolution 2
        calibrations.first.distortion,  # distortion 1
        calibrations.second.distortion,  # distortion 2
        desired_resolution,  # desired resolution - (width, height)
    )

    # Group all the transformations applied after rectification
    # These would be needed for 3D reconstrunction
    new_first_camera: np.ndarray = (
        affine_transform.dot(transforms.homographies.first)
        .dot(calibrations.first.camera_matrix)
        .dot(transforms.rotation.T)
    )

    new_second_camera: np.ndarray = (
        affine_transform.dot(transforms.homographies.second)
        .dot(calibrations.second.camera_matrix)
        .dot(calibrations.second.rotation)
        .dot(transforms.rotation.T)
    )

    updated_camera_matrices: Pair[np.ndarray] = Pair(
        first=new_first_camera,
        second=new_second_camera,
    )

    # OpenCV requires the final rotations applied
    updated_rotations: Pair[np.ndarray] = Pair(
        first=transforms.rotation,
        second=transforms.rotation.dot(calibrations.second.rotation.T),
    )

    updated_locations: Pair[np.ndarray] = Pair(
        first=np.zeros(3),
        second=np.array([calibrations.second.baseline, 0.0, 0.0]),
    )

    first_rectified: CameraCalibration = CameraCalibration(
        camera_matrix=updated_camera_matrices.first,
        distortion=np.zeros(5, dtype=np.float32),
        width=desired_resolution[0],
        height=desired_resolution[1],
        location=updated_locations.first,
        rotation=updated_rotations.first,
    )

    second_rectified: CameraCalibration = CameraCalibration(
        camera_matrix=updated_camera_matrices.second,
        distortion=np.zeros(5, dtype=np.float32),
        width=desired_resolution[0],
        height=desired_resolution[1],
        location=updated_locations.second,
        rotation=updated_rotations.second,
    )

    return Pair(first=first_rectified, second=second_rectified)


def compute_stereo_rectification(
    calibrations: Pair[CameraCalibration],
) -> StereoRectificationResult:
    """Encapsulates computation of the stereo rectification in a single function.
    For a given stereo calibration the function computes the rectifying transforms,
    rectified calibrations and pixel maps."""

    transforms: StereoRectificationTransforms = compute_rectifying_camera_transforms(
        calibrations
    )

    result: StereoRectificationResult = compute_rectifying_image_transforms(
        calibrations, transforms
    )

    return result


def rectify_image_pair(
    images: Pair[Image],
    rectification: StereoRectificationResult,
) -> Pair[Image]:
    """Rectifies two stereo images by appling the rectification map to them."""

    return Pair[Image](
        first=remap_image_pixels(images.first, rectification.pixel_maps.first),
        second=remap_image_pixels(images.second, rectification.pixel_maps.second),
    )


def _compute_common_affine_transform(
    first_camera_matrix: np.ndarray,
    second_camera_matrix: np.ndarray,
    first_homography: np.ndarray,
    second_homography: np.ndarray,
    first_dims: tuple[int, int],
    second_dims: tuple[int, int],
    first_distortion: Optional[np.ndarray] = None,
    second_distortion: Optional[np.ndarray] = None,
    desired_dims: Optional[tuple[int, int]] = None,
) -> np.ndarray:
    """
    Compute affine tranformation to fit the rectified images into desidered dimensions.

    After rectification usually the image is no more into the original image bounds.
    One can apply any transformation that do not affect disparity to fit the image into boundaries.
    This function corrects flipped images too.
    The algorithm may fail if one epipole is too close to the image.

    Parameters
    ----------
    first_camera_matrix, second_camera_matrix : numpy.ndarray
        3x3 original camera matrices of intrinsic parameters.
    first_homography, second_homography : numpy.ndarray
        3x3 rectifying transforms.
    first_dims, second_dims : tuple
        Resolution of images as (width, height) tuple.
    first_distortion, second_distortion : numpy.ndarray, optional
        Distortion coefficients in the order followed by OpenCV. If None is passed, zero distortion is
        assumed.
    desired_dims : tuple, optional
        Resolution of destination images as (width, height) tuple (default to the first image
        resolution).

    Returns
    -------
    numpy.ndarray
        3x3 affine transformation to be used both for the first and for the second camera.
    """

    if desired_dims is None:
        desired_dims = first_dims

    desired_width, desired_height = desired_dims

    first_corners: ImageCorners = get_image_corners(
        homography=first_homography,
        camera_matrix=first_camera_matrix,
        dimensions=first_dims,
        distortion=first_distortion,
    )

    second_corners: ImageCorners = get_image_corners(
        homography=second_homography,
        camera_matrix=second_camera_matrix,
        dimensions=second_dims,
        distortion=second_distortion,
    )

    min_x1: float = first_corners.min[0]
    max_x1: float = first_corners.max[0]

    min_x2: float = second_corners.min[0]
    max_x2: float = second_corners.max[0]

    min_y: float = min(first_corners.min[1], second_corners.min[1])
    max_y: float = max(first_corners.max[1], second_corners.max[1])

    # Flip factor
    flip_x: int = 1
    flip_y: int = 1

    if first_corners.top_left[0] > first_corners.top_right[0]:
        flip_x = -1
    if first_corners.top_left[1] > first_corners.bottom_left[1]:
        flip_y = -1

    # Scale X (choose common scale X to best fit bigger image between left and right)
    if max_x2 - min_x2 > max_x1 - min_x1:
        scale_x = flip_x * desired_width / (max_x2 - min_x2)
    else:
        scale_x = flip_x * desired_width / (max_x1 - min_x1)

    # Scale Y (unique not to lose rectification)
    scale_y = flip_y * desired_height / (max_y - min_y)

    # Translation X (keep always at left border)
    if flip_x == 1:
        translation_x = -min(min_x1, min_x2) * scale_x
    else:
        translation_x = -min(max_x1, max_x2) * scale_x

    # Translation Y (keep always at top border)
    if flip_y == 1:
        translation_y = -min_y * scale_y
    else:
        translation_y = -max_y * scale_y

    # Final affine transformation
    affine: np.ndarray = np.array(
        [[scale_x, 0, translation_x], [0, scale_y, translation_y], [0, 0, 1]]
    )

    return affine
