"""Module with helper functionality for stereo cameras."""

from dataclasses import dataclass
from typing import NamedTuple, Optional, Self

import cv2
import numpy as np

from ..camera import CameraCalibration, ImagePair

from .image_transformations import PixelMap, compute_pixel_map, remap_image_pixels
from .image_transformations import ImageCorners, get_image_corners



class StereoExtrinsics(NamedTuple):
    """Class representing stereo extrinsics."""

    location: np.ndarray
    rotation: np.ndarray


class StereoCalibration(NamedTuple):
    """Class representing a stereo camera."""

    master: CameraCalibration
    slave: CameraCalibration
    extrinsics: StereoExtrinsics

    @property
    def baseline(self: Self) -> float:
        """Returns the baseline between the two cameras."""
        return np.linalg.norm(self.extrinsics.location)


class StereoHomography(NamedTuple):
    """Class representing a rectifying transform."""

    rotation: np.ndarray  # common rotation for the two cameras
    master: np.ndarray  # homography for the master camera
    slave: np.ndarray  # homography for the slave camera


def compute_rectifying_homographies(calibration: StereoCalibration) -> StereoHomography:
    """
    Compute the rectifying homographies for a pair of sensors using the standard OpenCV algorithm.
    Adopted from: https://github.com/decadenza/SimpleStereo/blob/master/simplestereo/_rigs.py
    """

    resolution: tuple[int, int] = (calibration.master.width, calibration.master.height)

    rotation_master, rotation_slave, _, _, _, _, _ = cv2.stereoRectify(
        calibration.master.camera_matrix,  # 3x3 master camera matrix
        calibration.master.distortion,  # 5x1 master camera distortion
        calibration.slave.camera_matrix,  # 3x3 slave camera matrix
        calibration.slave.distortion,  # 5x1 slave camera distortion
        resolution,  # resolution (width, height)
        calibration.extrinsics.rotation,  # 3x3 rotation matrix from master to slave
        calibration.extrinsics.location,  # 3x1 translation vector from master to slave
        flags=0,
    )

    # OpenCV does not compute the rectifying homography, but a rotation in the object space.
    # R1 = Rnew * Rcam^{-1}
    # To get the homography:
    homography_master: np.ndarray = rotation_master.dot(
        np.linalg.inv(calibration.master.camera_matrix)
    )
    homography_slave: np.ndarray = rotation_slave.dot(
        np.linalg.inv(calibration.slave.camera_matrix)
    )

    # To get the common orientation, since the first camera has orientation as origin:
    # Rcommon = R1
    # It also can be retrieved from R2, cancelling the rotation of the second camera.
    # Rcommon = R2.dot(np.linalg.inv(rig.R))

    return StereoHomography(
        rotation=rotation_master,
        master=homography_master,
        slave=homography_slave,
    )


@dataclass
class RectificationResult:
    """Class representing a rectification map."""

    class Item(NamedTuple):

        # TODO: Add original calibration, and inverse pixel map
        calibration: CameraCalibration
        pixel_map: PixelMap
        location: np.ndarray
        rotation: np.ndarray

    homographies: StereoHomography
    master: Item
    slave: Item


def compute_rectifying_pixel_maps(
    calibration: StereoCalibration,
    homographies: StereoHomography,
) -> RectificationResult:
    """
    Computes updated camera matrices and pixel maps based on the given stereo calibration and
    rectifying homographies.
    Adopted from: https://github.com/decadenza/SimpleStereo/blob/master/simplestereo/_rigs.py
    """

    resolution_master: tuple[int, int] = (
        calibration.master.width,
        calibration.master.height,
    )
    resolution_slave: tuple[int, int] = (
        calibration.slave.width,
        calibration.slave.height,
    )

    desired_resolution: tuple[int, int] = resolution_master

    # Find fitting matrices, as additional correction of the new camera matrices (if any).
    # Useful e.g. to change destination image resolution or zoom.
    affine_transform: np.ndarray = _compute_common_affine_transform(
        calibration.master.camera_matrix,  # intrinsic 1
        calibration.slave.camera_matrix,  # intrinsic 2
        homographies.master,  # homography 1
        homographies.slave,  # homography 2
        resolution_master,  # resolution 1
        resolution_slave,  # resolution 2
        calibration.master.distortion,  # distortion 1
        calibration.slave.distortion,  # distortion 2
        desired_resolution,  # desired resolution - (width, height)
    )

    # Group all the transformations applied after rectification
    # These would be needed for 3D reconstrunction
    new_camera_master: np.ndarray = (
        affine_transform.dot(homographies.master)
        .dot(calibration.master.camera_matrix)
        .dot(homographies.rotation.T)
    )

    new_camera_slave: np.ndarray = (
        affine_transform.dot(homographies.slave)
        .dot(calibration.slave.camera_matrix)
        .dot(calibration.extrinsics.rotation)
        .dot(homographies.rotation.T)
    )

    # OpenCV requires the final rotations applied
    R1 = homographies.rotation
    R2 = homographies.rotation.dot(calibration.extrinsics.rotation.T)

    # Recompute final maps considering fitting transformations too
    master_pixel_map: PixelMap = compute_pixel_map(
        calibration.master.camera_matrix,
        calibration.master.distortion,
        R1,
        new_camera_master,
        desired_resolution,
    )

    slave_pixel_map: PixelMap = compute_pixel_map(
        calibration.slave.camera_matrix,
        calibration.slave.distortion,
        R2,
        new_camera_slave,
        desired_resolution,
    )

    # TODO: Figure out what to do with the extrinsics
    rectified_master: CameraCalibration = CameraCalibration(
        camera_matrix=new_camera_master,
        distortion=np.zeros(5, dtype=np.float32),
        width=desired_resolution[0],
        height=desired_resolution[1],
    )
    rectified_slave: CameraCalibration = CameraCalibration(
        camera_matrix=new_camera_slave,
        distortion=np.zeros(5, dtype=np.float32),
        width=desired_resolution[0],
        height=desired_resolution[1],
    )

    rectification_result: RectificationResult = RectificationResult(
        homographies=homographies,
        master=RectificationResult.Item(
            calibration=rectified_master,
            pixel_map=master_pixel_map,
            location=np.zeros(3),
            rotation=R1,
        ),
        slave=RectificationResult.Item(
            calibration=rectified_slave,
            pixel_map=slave_pixel_map,
            location=np.array([calibration.baseline, 0.0, 0.0]),
            rotation=R2,
        ),
    )

    return rectification_result


def compute_stereo_rectification(calibration: StereoCalibration) -> RectificationResult:
    """Compute a stereo rectification for the given stereo calibration."""

    # Estimate homographies that transforms the projections to the same plane
    homographies: StereoHomography = compute_rectifying_homographies(calibration)

    # Estimate transformations that rectify the image pixels
    rectification_result: RectificationResult = compute_rectifying_pixel_maps(
        calibration, homographies
    )

    return rectification_result


def rectify_image_pair(
    images: ImagePair,
    rectification: RectificationResult,
) -> ImagePair:
    """Rectifies two stereo images by appling the rectification map to them."""

    return ImagePair(
        first=remap_image_pixels(images.first, rectification.master.pixel_map),
        second=remap_image_pixels(images.second, rectification.slave.pixel_map),
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
        3x3 rectifying homographies.
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
