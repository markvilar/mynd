"""Module with helper functionality for reference data."""

from typing import Callable

import Metashape as ms
import numpy as np

from typing import Optional

from mynd.camera import CameraID, CameraReference
from mynd.collections import CameraGroup

from ..common.math import vector_to_array


def get_camera_reference_estimates(
    chunk: ms.Chunk,
) -> CameraGroup.References:
    """Returns the estimated references for the cameras in a chunk."""
    return collect_camera_references(
        chunk, callback=get_estimated_camera_reference
    )


def get_camera_reference_priors(chunk: ms.Chunk) -> CameraGroup.References:
    """Returns the prior references for the cameras in a chunk."""
    return collect_camera_references(chunk, callback=get_prior_camera_reference)


def collect_camera_references(
    chunk: ms.Chunk,
    callback: Callable[[ms.Camera], CameraReference],
) -> CameraGroup.References:
    """Iterates over the cameras in a chunk and collects the camera references."""
    reference_group: CameraGroup.References = CameraGroup.References()

    for camera in chunk.cameras:

        reference: Optional[CameraReference] = callback(camera)

        if reference is None:
            continue

        identifier: CameraID = CameraID(key=camera.key, label=camera.label)

        reference_group.identifiers.append(identifier)
        if reference.has_location():
            reference_group.locations[identifier] = reference.location
        if reference.has_rotation():
            reference_group.rotations[identifier] = reference.rotation

    return reference_group


def get_prior_camera_reference(camera: ms.Camera) -> Optional[CameraReference]:
    """Returns the prior reference of a camera if it has one and none otherwise."""

    if not camera.reference.enabled:
        return None

    if camera.reference.location_enabled:
        location: list = vector_to_array(camera.reference.location).tolist()
    else:
        location = None

    if camera.reference.rotation_enabled:
        rotation: list = vector_to_array(camera.reference.rotation).tolist()
    else:
        rotation = None

    return CameraReference(location, rotation)


def get_estimated_camera_reference(
    camera: ms.Camera,
) -> Optional[CameraReference]:
    """Returns reference statistics for the given camera. The function first selects
    a target CRS, a Cartesian CRS, and the transform to use, and then calculates the
    statistics with this configuration."""

    chunk: ms.Chunk = camera.chunk

    # If the camera is not aligned, the rest of the statistics
    if not camera.transform:
        return None

    # If the cameras are defined in a datum other than the chunk
    if chunk.camera_crs:
        transform: ms.Matrix = (
            ms.CoordinateSystem.datumTransform(chunk.crs, chunk.camera_crs)
            * chunk.transform.matrix
        )
    else:
        transform: ms.Matrix = chunk.transform.matrix

    # Get ECEF
    transform: ms.Matrix = _get_target_transform(camera)
    target_crs: ms.CoordinateSystem = _get_target_crs(camera)
    cartesian_crs: ms.CoordinateSystem = _get_cartesian_crs(target_crs)

    # Parameters: ecef_crs, target_crs, transform
    estimated_reference: CameraReference = compute_estimated_camera_reference(
        camera=camera,
        transform=transform,
        target_crs=target_crs,
        cartesian_crs=cartesian_crs,
    )

    return estimated_reference


def compute_estimated_camera_reference(
    camera: ms.Camera,
    transform: ms.Matrix,
    target_crs: ms.CoordinateSystem,
    cartesian_crs: ms.CoordinateSystem,
) -> CameraReference:
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

    return CameraReference(
        estimated_location.tolist(), estimated_rotation.tolist()
    )


def _get_target_transform(camera: ms.Camera) -> ms.Matrix:
    """Returns the target transform for a camera."""
    if camera.chunk.camera_crs:
        transform: ms.Matrix = (
            ms.CoordinateSystem.datumTransform(
                camera.chunk.crs, camera.chunk.camera_crs
            )
            * camera.chunk.transform.matrix
        )
    else:
        transform: ms.Matrix = camera.chunk.transform.matrix

    return transform


def _get_target_crs(camera: ms.Camera) -> ms.CoordinateSystem:
    """Returns the target coordinate system for the camera."""
    if camera.chunk.camera_crs:
        target_crs: ms.CoordinateSystem = camera.chunk.camera_crs
    else:
        target_crs: ms.CoordinateSystem = camera.chunk.crs

    return target_crs


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
