"""Module for executing registration tasks."""

import time

from functools import partial
from pathlib import Path

import numpy as np

from result import Ok, Err, Result

from benthoscan.spatial import (
    PointCloud,
    PointCloudLoader,
    read_point_cloud,
)

from benthoscan.spatial import (
    downsample_point_cloud,
    estimate_point_cloud_normals,
    generate_cascade_indices,
)

from benthoscan.spatial import (
    ExtendedRegistrationResult,
    register_point_cloud_fphp_fast,
    register_point_cloud_fphp_ransac,
    register_point_cloud_icp,
    register_point_cloud_graph,
)

from benthoscan.utils.log import logger

from .config_types import RegistrationTaskConfig


def prepare_point_cloud_loader(path: Path) -> PointCloudLoader:
    """Prepare point cloud loader by binding file path to the readers."""
    return partial(read_point_cloud, path=path)


def log_registration_task(config: RegistrationTaskConfig) -> None:
    """Logs information about the registration task."""

    logger.info("")
    logger.info("-------------------- REGISTRATION --------------------")
    for label, path in config.point_cloud_files.items():
        logger.info(f"Point cloud: {label}, {path}")
    logger.info("------------------------------------------------------")
    logger.info("")


def perform_pairwise_registration(
    source_loader: PointCloudLoader, target_loader: PointCloudLoader
) -> None:
    """Performs pairwise registration of two point clouds."""

    source_cloud: PointCloud = source_loader().unwrap()
    target_cloud: PointCloud = target_loader().unwrap()

    if not source_cloud.has_normals():
        source_cloud: PointCloud = estimate_point_cloud_normals(source_cloud)
    if not target_cloud.has_normals():
        target_cloud: PointCloud = estimate_point_cloud_normals(target_cloud)

    # NOTE: Parameters - move to config
    voxel_size: float = 0.10
    correspondence_distance = 0.30
    feature_radius: float = 0.60
    feature_neighbours: int = 200

    downsampled_source: PointCloud = downsample_point_cloud(
        source_cloud, spacing=voxel_size
    )
    downsampled_target: PointCloud = downsample_point_cloud(
        target_cloud, spacing=voxel_size
    )

    downsampled_source: PointCloud = estimate_point_cloud_normals(downsampled_source)
    downsampled_target: PointCloud = estimate_point_cloud_normals(downsampled_target)

    logger.info("Performing fast FPFH matching...")

    # Perform FPFH registration to get an initial estimate of the transformation between the
    # point clouds
    result: ExtendedRegistrationResult = register_point_cloud_fphp_fast(
        source=downsampled_source,
        target=downsampled_target,
        distance_threshold=correspondence_distance,
        feature_radius=feature_radius,
        feature_neighbours=feature_neighbours,
    )

    return result


def execute_point_cloud_registration(
    config: RegistrationTaskConfig,
) -> Result[None, str]:
    """Executes a point cloud registration task."""

    log_registration_task(config)

    loaders: list[PointCloudLoader] = list()
    for label, path in config.point_cloud_files.items():
        loaders.append(prepare_point_cloud_loader(path))

    count = len(loaders)
    if count < 2:
        return Err(f"invalid number of point clouds for registration: {count}")

    # TODO: Add index generate for dictionaries
    indices: list[MultiTargetIndex] = generate_cascade_indices(count)

    for index in indices:
        source: int = index.source
        for target in index.targets:

            start: float = time.time()
            result = perform_pairwise_registration(
                loaders[source],
                loaders[target],
            )
            end: float = time.time()

            elapsed: float = end - start

            logger.info("")
            logger.info(f"--------------------- FPFH registration --------------------")
            logger.info(f" - Source, target:        {source}, {target}")
            logger.info(f" - Elapsed time:          {elapsed}")
            logger.info(f" - Fast FPFH RMSE:        {result.inlier_rmse}")
            logger.info(f" - Fast FPFH fitness:     {result.fitness}")
            logger.info(f" - Fast FPFH corres.:     {len(result.correspondence_set)}")
            logger.info(f" - Fast FPFH trans.:      {result.transformation}")
            logger.info(f" - Fast FPFH info.:       {result.information}")
            logger.info(f"------------------------------------------------------------")
            logger.info("")

    # NOTE: Load all point clouds during development. In the final version point clouds
    # need to be loaded on use, due to memory constraints.

    match result:
        case Err(message):
            logger.error(message)
        case Ok(registration):
            logger.info(registration)

    # TODO: Set up registration schema
    # TODO: Build registration processes
    # TODO: Run registration processes

    raise NotImplementedError("execute_point_cloud_registration is not implemented")
