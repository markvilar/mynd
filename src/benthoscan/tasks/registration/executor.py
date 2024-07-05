"""Module for executing registration tasks."""

import time

from functools import partial
from pathlib import Path

import numpy as np

from result import Ok, Err, Result

from benthoscan.registration import (
    PointCloud,
    PointCloudLoader,
)

from benthoscan.registration import (
    downsample_point_cloud,
    estimate_point_cloud_normals,
    generate_cascade_indices,
)

from benthoscan.registration import (
    ExtendedRegistrationResult,
    register_point_cloud_fphp_fast,
    register_point_cloud_fphp_ransac,
    register_point_cloud_icp,
    register_point_cloud_graph,
)

from benthoscan.utils.log import logger

from .config_types import RegistrationTaskConfig


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
    voxel_size: float = 0.20
    correspondence_distance = 0.30
    feature_radius: float = 2.00
    feature_neighbours: int = 500
    sample_count = 3
    edge_length = 0.95
    normal_angle = 5.0
    max_iterations: int = 200000
    confidence: float = 0.9999
    estimate_scale: bool = True

    downsampled_source: PointCloud = downsample_point_cloud(
        source_cloud, spacing=voxel_size
    )
    downsampled_target: PointCloud = downsample_point_cloud(
        target_cloud, spacing=voxel_size
    )

    downsampled_source: PointCloud = estimate_point_cloud_normals(downsampled_source)
    downsampled_target: PointCloud = estimate_point_cloud_normals(downsampled_target)

    # Perform FPFH registration to get an initial estimate of the transformation between the
    # point clouds
    result: ExtendedRegistrationResult = register_point_cloud_fphp_ransac(
        source=downsampled_source,
        target=downsampled_target,
        distance_threshold=correspondence_distance,
        feature_radius=feature_radius,
        feature_neighbours=feature_neighbours,
        max_iterations=max_iterations,
        sample_count=sample_count,
        edge_check=edge_length,
        normal_check=normal_angle,
        scaling = estimate_scale
    )

    return result


def execute_point_cloud_registration(
    config: RegistrationTaskConfig,
) -> Result[None, str]:
    """Executes a point cloud registration task."""

    loaders: dict[int, PointCloudLoader] = config.point_cloud_loaders

    count = len(loaders)
    if count < 2:
        return Err(f"invalid number of point clouds for registration: {count}")

    # TODO: Add index generator for dictionaries
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
            logger.info(f"--------------------- Registration --------------------")
            logger.info(f" - Source, target:        {source}, {target}")
            logger.info(f" - Elapsed time:          {elapsed}")
            logger.info(f" - RMSE:                  {result.inlier_rmse}")
            logger.info(f" - Fitness:               {result.fitness}")
            logger.info(f" - Correspondences:       {len(result.correspondence_set)}")
            logger.info(f" - Transformation:        {result.transformation}")
            logger.info(f" - Infoformation:         {result.information}")
            logger.info(f"-------------------------------------------------------")
            logger.info("")

    match result:
        case Err(message):
            logger.error(message)
        case Ok(registration):
            logger.info(registration)

    # TODO: Set up registration schema
    # TODO: Build registration processes
    # TODO: Run registration processes

    raise NotImplementedError("execute_point_cloud_registration is not implemented")
