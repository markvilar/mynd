"""Module for chunk-related functionality."""

import Metashape as ms
import numpy as np

from mynd.collections import GroupID
from mynd.registration import RegistrationResult

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result

from .context import get_chunk_map
from .common.math import matrix_to_array


def apply_registration_results(
    target: GroupID, results: dict[GroupID, RegistrationResult]
) -> Result:
    """Updates Metashape chunks with the given registration results."""

    chunks: dict[GroupID, ms.Chunk] = get_chunk_map()

    if target not in chunks:
        return Err(f"missing target: {target}")

    target_chunk: ms.Chunk = chunks.get(target)

    for source, registration in results.items():

        source_chunk: ms.Chunk | None = chunks.get(source)

        if source_chunk is None:
            return Err(f"missing chunk: {source.label}")

        logger.info(
            f"Aligning chunks - target: {target_chunk.label}, source: {source_chunk.label}"
        )

        align_chunks(target_chunk, source_chunk, registration)

    return Ok(None)


def align_chunks(
    target: ms.Chunk, source: ms.Chunk, registration: RegistrationResult
) -> None:
    """Aligns the source chunk to the target with the given registration result.

    :arg target:        chunk that gets registered to
    :arg source:        chunk that gets registered from
    :arg registration:  registration result between the internal frames of the two chunks
    """

    update: np.ndarray = compute_aligning_transform(
        target, source, registration
    )

    # Update source chunk transform
    source.transform.matrix = source.transform.matrix * ms.Matrix(update)


def compute_aligning_transform(
    target: ms.Chunk, source: ms.Chunk, registration: RegistrationResult
) -> np.ndarray:
    """Computes an aligning transform based on a registration between the
    chunks local CRS. The computed transforms registers the source chunk
    to the target chunk."""

    # NOTE: Find a better name for these variables
    # T_source_inner: transform from internal coordinate to NED
    # T_source_local: ?????
    T_source_inner, T_source_local = get_point_cloud_transform(source)
    T_target_inner, T_target_local = get_point_cloud_transform(target)

    # Transformation to shift internal source CRS to internal target CRS
    shift_source_to_target: ms.Matrix = T_target_local * T_source_local.inv()

    # Combine shift between internal CRSs and registration correction to get the final correction
    correction: ms.Matrix = shift_source_to_target.inv() * ms.Matrix(
        registration.transformation
    )

    # NOTE: Write a comment about what this transform is!!!!!
    update: ms.Matrix = T_source_inner.inv() * correction * T_source_inner

    return matrix_to_array(update)


def get_point_cloud_transform(chunk: ms.Chunk) -> tuple[ms.Matrix, ms.Matrix]:
    """Gets the following transformations for a chunk:
    - transform from internal to NED
    - transform from geocentric to NED
    """

    if chunk.point_cloud.crs is None:
        world_crs: ms.CoordinateSystem = chunk.crs
        # World transform: chunk transform in world coordinate system (ECEF)
        world_transform: ms.Matrix = (
            chunk.transform.matrix * chunk.point_cloud.transform
        )
    else:
        world_crs = chunk.point_cloud.crs
        world_transform = chunk.point_cloud.transform

    origin = world_transform.translation()
    origin = world_crs.project(origin)

    # Set origin at height 0, i.e. mean sea level
    origin.z = 0
    origin = world_crs.unproject(origin)

    # Transform to convert geocentric coordinates to local coordinates
    local_transform: ms.Matrix = world_crs.localframe(origin)

    # Transform from internal to NED
    transform: ms.Matrix = local_transform * world_transform

    return transform, local_transform
