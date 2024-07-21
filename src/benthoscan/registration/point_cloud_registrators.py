"""Module for point cloud processors, i.e. including filters for spacing and confidence."""

from functools import partial
from typing import Optional

import numpy as np
import open3d
import open3d.geometry as geom
import open3d.pipelines.registration as reg

from benthoscan.utils.log import logger

from .point_cloud_types import PointCloud
from .point_cloud_loaders import PointCloudLoader
from .registration_types import (
    GlobalRegistrator,
    IncrementalRegistrator,
    ExtendedRegistrationResult,
)


def register_point_cloud_fphp_fast(
    source: PointCloud,
    target: PointCloud,
    distance_threshold: float,
    feature_radius: float = 1.50,
    feature_neighbours: int = 300,
) -> ExtendedRegistrationResult:
    """Registers the source to the target based on fast FPFH matching."""

    feature_extractor = partial(
        reg.compute_fpfh_feature,
        search_param=geom.KDTreeSearchParamHybrid(
            radius=feature_radius, max_nn=feature_neighbours
        ),
    )

    source_features: reg.Feature = feature_extractor(input=source)
    target_features: reg.Feature = feature_extractor(input=target)

    options: reg.FastGlobalRegistrationOption = reg.FastGlobalRegistrationOption(
        maximum_correspondence_distance=distance_threshold,
    )

    result: reg.RegistrationResult = reg.registration_fgr_based_on_feature_matching(
        source=source,
        target=target,
        source_feature=source_features,
        target_feature=target_features,
        option=options,
    )

    information: np.ndarray = reg.get_information_matrix_from_point_clouds(
        source=source,
        target=target,
        max_correspondence_distance=distance_threshold,
        transformation=result.transformation,
    )

    return ExtendedRegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=result.correspondence_set,
        transformation=result.transformation,
        information=information,
    )


def register_point_cloud_fphp_ransac(
    source: PointCloud,
    target: PointCloud,
    distance_threshold: float,
    feature_radius: float = 1.50,
    feature_neighbours: int = 900,
    mutual_filter: bool = True,
    sample_count: int = 3,
    max_iterations: int = 50000,
    confidence: float = 0.999,
    edge_check: Optional[float] = None,
    normal_check: Optional[float] = None,
    scaling: bool = False,
) -> ExtendedRegistrationResult:
    """Registers the source to the target based on FPFH matching."""

    feature_extractor = partial(
        reg.compute_fpfh_feature,
        search_param=geom.KDTreeSearchParamHybrid(
            radius=feature_radius, max_nn=feature_neighbours
        ),
    )

    source_features: reg.Feature = feature_extractor(input=source)
    target_features: reg.Feature = feature_extractor(input=target)

    estimator: reg.TransformationEstimation = reg.TransformationEstimationPointToPoint(
        with_scaling=scaling
    )

    checkers: list[CorrespondenceChecker] = [
        reg.CorrespondenceCheckerBasedOnDistance(distance_threshold),
    ]

    if edge_check:
        checkers.append(reg.CorrespondenceCheckerBasedOnEdgeLength(edge_check))
    if normal_check:
        checkers.append(reg.CorrespondenceCheckerBasedOnNormal(normal_check))

    convergence = reg.RANSACConvergenceCriteria(
        max_iteration=max_iterations,
        confidence=confidence,
    )

    result: reg.RegistrationResult = reg.registration_ransac_based_on_feature_matching(
        source=source,
        target=target,
        source_feature=source_features,
        target_feature=target_features,
        max_correspondence_distance=distance_threshold,
        mutual_filter=mutual_filter,
        estimation_method=estimator,
        ransac_n=sample_count,
        checkers=checkers,
        criteria=convergence,
    )

    information = reg.get_information_matrix_from_point_clouds(
        source,
        target,
        distance_threshold,
        result.transformation,
    )

    return ExtendedRegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=result.correspondence_set,
        transformation=result.transformation,
        information=information,
    )


def register_point_cloud_icp(
    source: PointCloud,
    target: PointCloud,
    distance_threshold: float,
    transformation: np.ndarray,
    distance_measure: reg.TransformationEstimation = reg.TransformationEstimationPointToPlane(),
) -> ExtendedRegistrationResult:
    """Registers the source to the target with ICP."""

    if not source.has_normals():
        return Err("source point cloud does not have normals")

    if not target.has_normals():
        return Err("target point cloud does not have normals")

    result: reg.RegistrationResult = reg.registration_icp(
        source,
        target,
        distance_threshold,
        transformation,
        distance_measure,
    )

    information = reg.get_information_matrix_from_point_clouds(
        source,
        target,
        distance_threshold,
        result.transformation,
    )

    return ExtendedRegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=result.correspondence_set,
        transformation=result.transformation,
        information=information,
    )


def build_pose_graph(
    results: dict[int, dict[int, ExtendedRegistrationResult]],
) -> reg.PoseGraph:
    """Builds a pose graph from registered point clouds."""

    odometry = np.identity(4)

    pose_graph = reg.PoseGraph()
    pose_graph.nodes.append(reg.PoseGraphNode(odometry))

    for source_id, registrations in results.items():

        for target_id, result in registrations.items():

            if target_id == source_id + 1:  # odometry case

                odometry = np.dot(result.transformation, odometry)

                pose_graph.nodes.append(
                    reg.PoseGraphNode(
                        np.linalg.inv(odometry),
                    )
                )
                pose_graph.edges.append(
                    reg.PoseGraphEdge(
                        source_id,
                        target_id,
                        result.transformation,
                        result.information,
                        uncertain=False,
                    )
                )
            else:  # loop closure case
                pose_graph.edges.append(
                    reg.PoseGraphEdge(
                        source_id,
                        target_id,
                        result.transformation,
                        result.information,
                        uncertain=True,
                    )
                )

    return pose_graph


def optimize_pose_graph(
    pose_graph: reg.PoseGraph,
    correspondence_distance: float,
    prune_threshold: float,
    preference_loop_closure: float,
    reference_node: int = -1,
) -> reg.PoseGraph:
    """Optimizes a pose graph by optimizing and pruning graph edges."""

    method = reg.GlobalOptimizationLevenbergMarquardt()

    criteria = reg.GlobalOptimizationConvergenceCriteria()

    option = reg.GlobalOptimizationOption(
        max_correspondence_distance=correspondence_distance,
        edge_prune_threshold=prune_threshold,
        preference_loop_closure=preference_loop_closure,
        reference_node=reference_node,
    )

    reg.global_optimization(
        pose_graph,
        method,
        criteria,
        option,
    )

    return pose_graph
