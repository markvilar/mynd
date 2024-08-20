"""Module with helper functionality for stereo cameras."""

from dataclasses import dataclass
from typing import NamedTuple, Optional, Self

import cv2
import numpy as np

from ..utils.log import logger


class CameraCalibration(NamedTuple):
    """Class representing a camera calibration."""

    camera_matrix: np.ndarray
    distortion: np.ndarray
    width: int
    height: int

    @property
    def focal_length(self: Self) -> float:
        """Returns the focal length from a camera calibration."""
        return self.camera_matrix[0,0]

    @property
    def optical_center(self: Self) -> tuple[float, float]:
        """Returns the optical center for the camera calibration."""
        return (self.camera_matrix[0,2], self.camera_matrix[1,2])

    @property
    def image_size(self: Self) -> tuple[int, int]:
        """Returns the image size as height, width."""
        return (self.height, self.width)


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

    rotation: np.ndarray    # common rotation for the two cameras
    master: np.ndarray      # homography for the master camera
    slave: np.ndarray       # homography for the slave camera


def compute_rectifying_homographies(calibration: StereoCalibration) -> StereoHomography:
    """
    Compute the rectifying homographies for a pair of sensors using the standard OpenCV algorithm.
    Adopted from: https://github.com/decadenza/SimpleStereo/blob/master/simplestereo/_rigs.py
    """

    resolution: tuple[int, int] = (calibration.master.width, calibration.master.height)

    rotation_master, rotation_slave, _, _, _, _, _ = cv2.stereoRectify(
        calibration.master.camera_matrix,   # 3x3 master camera matrix
        calibration.master.distortion,      # 5x1 master camera distortion
        calibration.slave.camera_matrix,    # 3x3 slave camera matrix
        calibration.slave.distortion,       # 5x1 slave camera distortion
        resolution,                         # resolution (width, height)
        calibration.extrinsics.rotation,    # 3x3 rotation matrix from master to slave
        calibration.extrinsics.location,    # 3x1 translation vector from master to slave
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

        calibration: CameraCalibration
        pixel_maps: tuple[np.ndarray, np.ndarray]
        location: np.ndarray
        rotation: np.ndarray

    # TODO: Add original calibration
    homographies: StereoHomography
    master: Item
    slave: Item


def compute_rectifying_pixel_maps(
    calibration: StereoCalibration,
    homographies: StereoHomography,
) -> RectificationResult:
    """
    Computes updated camera matrices and pixel maps based on the given calibration and 
    homographies.
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

    alpha: float = 1.0

    # Find fitting matrices, as additional correction of the new camera matrices (if any).
    # Useful e.g. to change destination image resolution or zoom.
    affine_transform: np.ndarray = _estimate_affine_image_transform(
        calibration.master.camera_matrix,  # intrinsic 1
        calibration.slave.camera_matrix,  # intrinsic 2
        homographies.master,  # homography 1
        homographies.slave,  # homography 2
        resolution_master,  # resolution 1
        resolution_slave,  # resolution 2
        calibration.master.distortion,  # distortion 1
        calibration.slave.distortion,  # distortion 2
        desired_resolution,  # desired resolution - (width, height)
        alpha,  # scaling factor
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
    pixel_maps_master: tuple[np.ndarray, np.ndarray] = cv2.initUndistortRectifyMap(
        calibration.master.camera_matrix,
        calibration.master.distortion,
        R1,
        new_camera_master,
        desired_resolution,
        cv2.CV_32FC1,
    )
    pixel_maps_slave: tuple[np.ndarray, np.ndarray] = cv2.initUndistortRectifyMap(
        calibration.slave.camera_matrix,
        calibration.slave.distortion,
        R2,
        new_camera_slave,
        desired_resolution,
        cv2.CV_32FC1,
    )

    # TODO: Figure out what to do with the extrinsics
    rectified_master = CameraCalibration(
        camera_matrix = new_camera_master,
        distortion = np.zeros(5, dtype=np.float32),
        width = desired_resolution[0],
        height = desired_resolution[1],
    )
    rectified_slave = CameraCalibration(
        camera_matrix = new_camera_slave,
        distortion = np.zeros(5, dtype=np.float32),
        width = desired_resolution[0],
        height = desired_resolution[1],
    )

    rectification_result: RectificationResult = RectificationResult(
        homographies=homographies,
        master=RectificationResult.Item(
            calibration=rectified_master,
            pixel_maps=pixel_maps_master,
            location=np.zeros(3),
            rotation=R1,
        ),
        slave=RectificationResult.Item(
            calibration=rectified_slave,
            pixel_maps=pixel_maps_slave,
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
    rectification_result: RectificationResult = compute_rectifying_pixel_maps(calibration, homographies)

    return rectification_result


def rectify_image_pair(
    master_image: np.ndarray,
    slave_image: np.ndarray,
    rectification: RectificationResult,
) -> tuple[np.ndarray, np.ndarray]:
    """Rectifies two stereo images by appling the rectification map to them."""

    rectified_master: np.ndarray = cv2.remap(
        master_image,
        rectification.master.pixel_maps[0],
        rectification.master.pixel_maps[1],
        cv2.INTER_LINEAR,
    )
    rectified_slave: np.ndarray = cv2.remap(
        slave_image,
        rectification.slave.pixel_maps[0],
        rectification.slave.pixel_maps[1],
        cv2.INTER_LINEAR,
    )

    return rectified_master, rectified_slave


# TODO: Adapt code to use this class for readability
class ImageCorners(NamedTuple):
    """Class representing image corners."""

    top_left: tuple[int, int]  # corners[0,0] = [0,0]
    top_right: tuple[int, int]  # corners[1,0] = [dims[0]-1,0]
    bottom_right: tuple[int, int]  # corners[2,0] = [dims[0]-1,dims[1]-1]
    bottom_left: tuple[int, int]  # corners[3,0] = [0, dims[1]-1]


def _getCorners(
    H: np.ndarray,
    intrinsicMatrix: np.ndarray,
    dims: tuple[int, int],
    distCoeffs: Optional[np.ndarray] = None,
) -> list[tuple[int, int]]:
    """
    Get points on the image borders after distortion correction and a rectification 
    transformation.

    Parameters
    ----------
    H : numpy.ndarray
        3x3 rectification homography.
    intrinsicMatrix : numpy.ndarray
        3x3 camera matrix of intrinsic parameters.
    dims : tuple
        Image dimensions in pixels as (width, height).
    distCoeffs : numpy.ndarray or None
        Distortion coefficients (default to None).

    Returns
    -------
    tuple
        Corners of the image clockwise from top-left.
    """
    if distCoeffs is None:
        distCoeffs = np.zeros(5)

    # Set image corners in the form requested by cv2.undistortPoints
    corners = np.zeros((4, 1, 2), dtype=np.float32)
    corners[0, 0] = [0, 0]  # Top left
    corners[1, 0] = [dims[0] - 1, 0]  # Top right
    corners[2, 0] = [dims[0] - 1, dims[1] - 1]  # Bottom right
    corners[3, 0] = [0, dims[1] - 1]  # Bottom left
    undist_rect_corners = cv2.undistortPoints(
        corners, intrinsicMatrix, distCoeffs, R=H.dot(intrinsicMatrix)
    )

    [(x, y) for x, y in np.squeeze(undist_rect_corners)]

    return [(x, y) for x, y in np.squeeze(undist_rect_corners)]


def _estimate_affine_image_transform(
    intrinsicMatrix1: np.ndarray,
    intrinsicMatrix2: np.ndarray,
    H1: np.ndarray,
    H2: np.ndarray,
    dims1: tuple[int, int],
    dims2: tuple[int, int],
    distCoeffs1: Optional[np.ndarray] = None,
    distCoeffs2: Optional[np.ndarray] = None,
    destDims: Optional[tuple[int, int]] = None,
    alpha: Optional[float] = 1,
) -> np.ndarray:
    """
    Compute affine tranformation to fit the rectified images into desidered dimensions.

    After rectification usually the image is no more into the original image bounds.
    One can apply any transformation that do not affect disparity to fit the image into boundaries.
    This function corrects flipped images too.
    The algorithm may fail if one epipole is too close to the image.

    Parameters
    ----------
    intrinsicMatrix1, intrinsicMatrix2 : numpy.ndarray
        3x3 original camera matrices of intrinsic parameters.
    H1, H2 : numpy.ndarray
        3x3 rectifying homographies.
    dims1, dims2 : tuple
        Resolution of images as (width, height) tuple.
    distCoeffs1, distCoeffs2 : numpy.ndarray, optional
        Distortion coefficients in the order followed by OpenCV. If None is passed, zero distortion is 
        assumed.
    destDims : tuple, optional
        Resolution of destination images as (width, height) tuple (default to the first image 
        resolution).
    alpha : float, optional
        Scaling parameter between 0 and 1 to be applied to both images. If alpha=1 (default), the 
        corners of the original
        images are preserved. If alpha=0, only valid rectangle is made visible.
        Intermediate values produce a result in the middle. Extremely skewed camera positions
        do not work well with alpha<1.

    Returns
    -------
    numpy.ndarray
        3x3 affine transformation to be used both for the first and for the second camera.
    """

    if destDims is None:
        destDims = dims1

    # Get border points
    tL1, tR1, bR1, bL1 = _getCorners(H1, intrinsicMatrix1, dims1, distCoeffs1)
    tL2, tR2, bR2, bL2 = _getCorners(H2, intrinsicMatrix2, dims2, distCoeffs2)

    minX1 = min(tR1[0], bR1[0], bL1[0], tL1[0])
    minX2 = min(tR2[0], bR2[0], bL2[0], tL2[0])
    maxX1 = max(tR1[0], bR1[0], bL1[0], tL1[0])
    maxX2 = max(tR2[0], bR2[0], bL2[0], tL2[0])

    minY = min(tR2[1], bR2[1], bL2[1], tL2[1], tR1[1], bR1[1], bL1[1], tL1[1])
    maxY = max(tR2[1], bR2[1], bL2[1], tL2[1], tR1[1], bR1[1], bL1[1], tL1[1])

    # Flip factor
    flipX = 1
    flipY = 1
    if tL1[0] > tR1[0]:
        flipX = -1
    if tL1[1] > bL1[1]:
        flipY = -1

    # Scale X (choose common scale X to best fit bigger image between left and right)
    if maxX2 - minX2 > maxX1 - minX1:
        scaleX = flipX * destDims[0] / (maxX2 - minX2)
    else:
        scaleX = flipX * destDims[0] / (maxX1 - minX1)

    # Scale Y (unique not to lose rectification)
    scaleY = flipY * destDims[1] / (maxY - minY)

    # Translation X (keep always at left border)
    if flipX == 1:
        tX = -min(minX1, minX2) * scaleX
    else:
        tX = -min(maxX1, maxX2) * scaleX

    # Translation Y (keep always at top border)
    if flipY == 1:
        tY = -minY * scaleY
    else:
        tY = -maxY * scaleY

    # Final affine transformation
    Fit = np.array([[scaleX, 0, tX], [0, scaleY, tY], [0, 0, 1]])

    if alpha >= 1:
        # Preserve all image corners
        return Fit

    if alpha < 0:
        alpha = 0

    # Find inner rectangle for both images
    tL1, tR1, bR1, bL1 = _getCorners(
        Fit.dot(H1), intrinsicMatrix1, destDims, distCoeffs1
    )
    tL2, tR2, bR2, bL2 = _getCorners(
        Fit.dot(H2), intrinsicMatrix2, destDims, distCoeffs2
    )

    left = max(tL1[0], bL1[0], tL2[0], bL2[0])
    right = min(tR1[0], bR1[0], tR2[0], bR2[0])
    top = max(tL1[1], tR1[1], tL2[1], tR2[1])
    bottom = min(bL1[1], bR1[1], bL2[1], bR2[1])

    s = max(
        destDims[0] / (right - left), destDims[1] / (bottom - top)
    )  # Extra scaling parameter
    s = (s - 1) * (1 - alpha) + 1  # As linear function of alpha

    K = np.eye(3)
    K[0, 0] = K[1, 1] = s
    K[0, 2] = -s * left
    K[1, 2] = -s * top

    return K.dot(Fit)
