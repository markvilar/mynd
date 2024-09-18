"""Module with helper functionality for reference data."""

from dataclasses import dataclass

import Metashape as ms
import numpy as np

from typing import Optional

from mynd.api import CameraReferenceGroup
from ..utils.math import vector_to_array


def get_reference_group(chunk: ms.Chunk) -> CameraReferenceGroup:
    """Returns the camera references in a Metashape chunk."""

    group: CameraReferenceGroup = CameraReferenceGroup()
    for camera in chunk.cameras:

        references: CameraReferenceStats = compute_camera_reference_stats(camera)

        if references.aligned_location is not None:
            group.aligned_locations[camera.key] = references.aligned_location

        if references.aligned_rotation is not None:
            group.aligned_rotations[camera.key] = references.aligned_rotation

        if references.prior_location is not None:
            group.prior_locations[camera.key] = references.prior_location

        if references.prior_rotation is not None:
            group.prior_rotations[camera.key] = references.prior_rotation

    return group


@dataclass
class CameraReferenceStats:
    """Class representing a camera transform. Internal data class used for readability."""

    aligned_location: Optional[np.ndarray] = None
    aligned_rotation: Optional[np.ndarray] = None

    prior_location: Optional[np.ndarray] = None
    prior_rotation: Optional[np.ndarray] = None

    error_location: Optional[np.ndarray] = None
    error_rotation: Optional[np.ndarray] = None


def compute_camera_reference_stats(camera: ms.Camera) -> CameraReferenceStats:
    """Returns reference statistics for the given camera. The function first selects
    a target CRS, a Cartesian CRS, and the transform to use, and then calculates the
    statistics with this configuration."""

    chunk: ms.Chunk = camera.chunk

    stats: CameraReferenceStats = CameraReferenceStats()

    if camera.reference.location:
        stats.prior_location = vector_to_array(camera.reference.location)
    if camera.reference.rotation:
        stats.prior_rotation = vector_to_array(camera.reference.rotation)

    # If the camera is not aligned, the rest of the statistics
    if not camera.transform:
        return stats

    # If the cameras are defined in a datum other than the chunk
    if chunk.camera_crs:
        transform: ms.Matrix = (
            ms.CoordinateSystem.datumTransform(chunk.crs, chunk.camera_crs)
            * chunk.transform.matrix
        )
        target_crs: ms.CoordinateSystem = chunk.camera_crs
    else:
        transform: ms.Matrix = chunk.transform.matrix
        target_crs: ms.CoordinateSystem = chunk.crs

    # Get ECEF
    cartesian_crs: ms.CoordinateSystem = _get_cartesian_crs(target_crs)

    # Parameters: ecef_crs, target_crs, transform
    aligned_location, aligned_rotation = _compute_aligned_reference(
        camera=camera,
        transform=transform,
        target_crs=target_crs,
        cartesian_crs=cartesian_crs,
    )

    # TODO: Compute location error / variance
    # TODO: Compute rotation error / variance

    stats.aligned_location: np.ndarray = aligned_location
    stats.aligned_rotation: np.ndarray = aligned_rotation

    return stats


def _compute_aligned_reference(
    camera: ms.Camera,
    transform: ms.Matrix,
    target_crs: ms.CoordinateSystem,
    cartesian_crs: ms.CoordinateSystem,
) -> tuple[np.ndarray, np.ndarray]:
    """Computes the location and rotation for an aligned camera to the target CRS.
    The Cartesian CRS is used as a common intermediate CRS, while the return
    references are converted to the target CRS."""

    # Transformation from camera to ECEF (but without proper rotation)
    camera_transform: ms.Matrix = transform * camera.transform
    antenna_transform: ms.Matrix = _get_antenna_transform(camera.sensor)

    # Compensate for antenna lever arm
    location_ecef: ms.Vector = (
        camera_transform.translation()
        + camera_transform.rotation() * antenna_transform.translation()
    )
    rotation_ecef: ms.Matrix = (
        camera_transform.rotation() * antenna_transform.rotation()
    )

    # Get orientation relative to local frame
    if (
        camera.chunk.euler_angles == ms.EulerAnglesOPK
        or camera.chunk.euler_angles == ms.EulerAnglesPOK
    ):
        localframe: ms.Matrix = target_crs.localframe(location_ecef)
    else:
        localframe: ms.Matrix = cartesian_crs.localframe(location_ecef)

    # Convert the location from Cartesian CRS to target CRS
    estimated_location: ms.Vector = ms.CoordinateSystem.transform(
        location_ecef, cartesian_crs, target_crs
    )

    # Compute estimate rotation as matrix and vector
    estimated_rotation: ms.Vector = ms.utils.mat2euler(
        localframe.rotation() * rotation_ecef, camera.chunk.euler_angles
    )

    estimated_location: np.ndarray = vector_to_array(estimated_location)
    estimated_rotation: np.ndarray = vector_to_array(estimated_rotation)

    return estimated_location, estimated_rotation


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
