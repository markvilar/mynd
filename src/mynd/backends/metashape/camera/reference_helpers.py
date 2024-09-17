"""Module with helper functionality for reference data."""

import Metashape as ms
import numpy as np

from typing import NamedTuple, Optional

from ..utils.math import matrix_to_array, vector_to_array


class CameraReferenceStats(NamedTuple):
    """Class representing a camera transform. Internal data class used for readability."""

    aligned_location: np.ndarray  # location vector
    aligned_rotation: np.ndarray  # rotation matrix

    prior_location: Optional[np.ndarray] = None  # location vector
    prior_rotation: Optional[np.ndarray] = None  # rotation matrix


def camera_reference_stats(
    camera: ms.Camera,
) -> Optional[CameraReferenceStats]:
    """Returns reference statistics for the given camera. The function first selects
    a target CRS, a Cartesian CRS, and the transform to use, and then calculates the
    statistics with this configuration. Returns None if the camera is not aligned."""

    chunk: ms.Chunk = camera.chunk

    # If the camera is not align, return
    if not camera.transform:
        return None

    transform: ms.Matrix = chunk.transform.matrix
    crs: ms.CoordinateSystem = chunk.crs

    # If the cameras are defined in a datum other than the chunk
    if chunk.camera_crs:
        transform: ms.Matrix = (
            ms.CoordinateSystem.datumTransform(crs, chunk.camera_crs) * transform
        )
        crs: ms.CoordinateSystem = chunk.camera_crs

    # Get ECEF
    ecef_crs: ms.CoordinateSystem = _get_cartesian_crs(crs)

    # Parameters: ecef_crs, target_crs, transform
    statistics: CameraReferenceStats = _compute_camera_reference_stats(
        camera=camera,
        transform=transform,
        target_crs=crs,
        cartesian_crs=ecef_crs,
    )

    return statistics


def _compute_camera_reference_stats(
    camera: ms.Camera,
    transform: ms.Matrix,
    target_crs: ms.CoordinateSystem,
    cartesian_crs: ms.CoordinateSystem,
) -> CameraReferenceStats:
    """Computes reference statistics for the given camera. The Cartesian CRS is used
    as a common intermediate CRS, while the return references are converted to the
    target CRS."""

    chunk: ms.Chunk = camera.chunk

    # Transformation from camera to ECEF (but without proper rotation)
    camera_transform: ms.Matrix = transform * camera.transform
    antenna_transform: ms.Matrix = _get_antenna_transform(camera.sensor)

    # Get reference location and rotation (antenna) in ECEF
    location_ecef: ms.Vector = (
        camera_transform.translation()
        + camera_transform.rotation() * antenna_transform.translation()
    )
    rotation_ecef: ms.Matrix = (
        camera_transform.rotation() * antenna_transform.rotation()
    )

    # Get orientation relative to local frame
    if (
        chunk.euler_angles == ms.EulerAnglesOPK
        or chunk.euler_angles == ms.EulerAnglesPOK
    ):
        localframe: ms.Matrix = target_crs.localframe(location_ecef)
    else:
        localframe: ms.Matrix = cartesian_crs.localframe(location_ecef)

    # Convert the location from Cartesian CRS to target CRS
    estimated_location: ms.Vector = ms.CoordinateSystem.transform(
        location_ecef, cartesian_crs, target_crs
    )

    # Compute estimate rotation as matrix and vector
    estimated_rotation_mat: ms.Matrix = localframe.rotation() * rotation_ecef
    estimated_rotation_vec: ms.Vector = ms.utils.mat2euler(
        estimated_rotation_mat, chunk.euler_angles
    )

    estimated_location: np.ndarray = vector_to_array(estimated_location)
    estimated_rotation_mat: np.ndarray = matrix_to_array(estimated_rotation_mat)
    estimated_rotation_vec: np.ndarray = vector_to_array(estimated_rotation_vec)

    # TODO: Compute estimated location and rotation in local coordinates

    if camera.reference.location:
        # TODO: Get prior location
        pass

    if camera.reference.rotation:
        # TODO: Get prior rotation
        pass

    if camera.location_covariance:
        # TODO: Compute location error covariance
        pass

    if camera.rotation_covariance:
        # TODO: Compute rotation error covariance
        pass

    # TODO: Compute location error / variance
    # TODO: Compute rotation error / variance

    return CameraReferenceStats(estimated_location, estimated_rotation_vec)


def _get_cartesian_crs(crs: ms.CoordinateSystem) -> ms.CoordinateSystem:
    """Returns a Cartesian coordinate reference system."""
    ecef_crs: ms.CoordinateSystem = crs.geoccs
    if ecef_crs is None:
        ecef_crs: ms.CoordinateSystem = ms.CoordinateSystem("LOCAL")
    return ecef_crs


def _get_antenna_transform(sensor: ms.Sensor) -> ms.Matrix:
    """Returns the GPS antenna transform for a Metashape sensor."""
    location: ms.Vector = sensor.antenna.location

    if location is None:
        location: ms.Vector = sensor.antenna.location_ref
    if location is None:
        location: ms.Vector = ms.Vector([0.0, 0.0, 0.0])

    rotation: ms.Matrix = sensor.antenna.rotation

    if rotation is None:
        rotation: ms.Vector = sensor.antenna.rotation_ref
    if rotation is None:
        rotation: ms.Vector = ms.Vector([0.0, 0.0, 0.0])
    transform: ms.Matrix = (
        ms.Matrix.Diag((1, -1, -1, 1))
        * ms.Matrix.Translation(location)
        * ms.Matrix.Rotation(ms.Utils.ypr2mat(rotation))
    )
    return transform


"""
def compute_aligned_reference_updated() -> None:
    if not camera.transform:
        return

    transform = chunk.transform.matrix
    crs = chunk.crs

    if chunk.camera_crs:
        transform = Metashape.CoordinateSystem.datumTransform(crs, chunk.camera_crs) * transform
        crs = chunk.camera_crs

    ecef_crs = self.getCartesianCrs(crs)

    camera_transform = transform * camera.transform
    antenna_transform = self.getAntennaTransform(camera.sensor)
    location_ecef = camera_transform.translation() + camera_transform.rotation() * antenna_transform.translation()
    rotation_ecef = camera_transform.rotation() * antenna_transform.rotation()

    self.estimated_location = Metashape.CoordinateSystem.transform(location_ecef, ecef_crs, crs)
    if camera.reference.location:
        self.reference_location = camera.reference.location
        self.error_location = Metashape.CoordinateSystem.transform(self.estimated_location, crs, ecef_crs) - Metashape.CoordinateSystem.transform(self.reference_location, crs, ecef_crs)
        self.error_location = crs.localframe(location_ecef).rotation() * self.error_location

    if chunk.euler_angles == Metashape.EulerAnglesOPK or chunk.euler_angles == Metashape.EulerAnglesPOK:
        localframe = crs.localframe(location_ecef)
    else:
        localframe = ecef_crs.localframe(location_ecef)

    self.estimated_rotation = Metashape.utils.mat2euler(localframe.rotation() * rotation_ecef, chunk.euler_angles)
    if camera.reference.rotation:
        self.reference_rotation = camera.reference.rotation
        self.error_rotation = self.estimated_rotation - self.reference_rotation
        self.error_rotation.x = (self.error_rotation.x + 180) % 360 - 180
        self.error_rotation.y = (self.error_rotation.y + 180) % 360 - 180
        self.error_rotation.z = (self.error_rotation.z + 180) % 360 - 180

    if camera.location_covariance:
        T = crs.localframe(location_ecef) * transform
        R = T.rotation() * T.scale()

        cov = R * camera.location_covariance * R.t()
        self.sigma_location = Metashape.Vector([math.sqrt(cov[0, 0]), math.sqrt(cov[1, 1]), math.sqrt(cov[2, 2])])

    if camera.rotation_covariance:
        T = localframe * camera_transform  # to reflect rotation angles ypr (ecef_crs.localfram) or opk (crs.localframe)
        R0 = T.rotation()

        dR = antenna_transform.rotation()

        da = Metashape.utils.dmat2euler(R0 * dR, R0 * self.makeRotationDx(0) * dR, chunk.euler_angles);
        db = Metashape.utils.dmat2euler(R0 * dR, R0 * self.makeRotationDy(0) * dR, chunk.euler_angles);
        dc = Metashape.utils.dmat2euler(R0 * dR, R0 * self.makeRotationDz(0) * dR, chunk.euler_angles);

        R = Metashape.Matrix([da, db, dc]).t()

        cov = R * camera.rotation_covariance * R.t()

        self.sigma_rotation = Metashape.Vector([math.sqrt(cov[0, 0]), math.sqrt(cov[1, 1]), math.sqrt(cov[2, 2])])

def getCartesianCrs(self, crs):
    ecef_crs = crs.geoccs
    if ecef_crs is None:
        ecef_crs = Metashape.CoordinateSystem('LOCAL')
    return ecef_crs

def getAntennaTransform(self, sensor):
    location = sensor.antenna.location
    if location is None:
        location = sensor.antenna.location_ref
    if location is None:
        location = Metashape.Vector([0.0, 0.0, 0.0])
    rotation = sensor.antenna.rotation
    if rotation is None:
        rotation = sensor.antenna.rotation_ref
    if rotation is None:
        rotation = Metashape.Vector([0.0, 0.0, 0.0])
    return Metashape.Matrix.Diag((1, -1, -1, 1)) * Metashape.Matrix.Translation(location) * Metashape.Matrix.Rotation(Metashape.Utils.ypr2mat(rotation))

def makeRotationDx(self, alpha):
    sina = math.sin(alpha)
    cosa = math.cos(alpha)
    return Metashape.Matrix([[0, 0, 0], [0, -sina, -cosa], [0, cosa, -sina]])

def makeRotationDy(self, alpha):
    sina = math.sin(alpha)
    cosa = math.cos(alpha)
    return Metashape.Matrix([[-sina, 0, cosa], [0, 0, 0], [-cosa, 0, -sina]])

def makeRotationDz(self, alpha):
    sina = math.sin(alpha)
    cosa = math.cos(alpha)
    return Metashape.Matrix([[-sina, -cosa, 0], [cosa, -sina, 0], [0, 0, 0]])
"""
