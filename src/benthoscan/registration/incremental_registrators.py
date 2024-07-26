"""Module for incremental point cloud registrators."""

import numpy as np
import open3d.pipelines.registration as reg

from .data_types import PointCloud, RegistrationResult


def register_icp(
    source: PointCloud,
    target: PointCloud,
    transformation: np.ndarray,
    *,
    distance_threshold: float,
    estimation_method: reg.TransformationEstimation = reg.TransformationEstimationPointToPlane(),
    criteria: reg.ICPConvergenceCriteria = reg.ICPConvergenceCriteria(),
) -> RegistrationResult:
    """Registers the source to the target with ICP."""

    result: reg.RegistrationResult = reg.registration_icp(
        source=source,
        target=target,
        init=transformation,
        max_correspondence_distance=distance_threshold,
        estimation_method=estimation_method,
        criteria=criteria,
    )

    information: np.ndarray = reg.get_information_matrix_from_point_clouds(
        source=source,
        target=target,
        max_correspondence_distance=distance_threshold,
        transformation=result.transformation,
    )

    return RegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=result.correspondence_set,
        transformation=result.transformation,
        information=information,
    )


def register_colored_icp(
    source: PointCloud,
    target: PointCloud,
    transformation: np.ndarray,
    *,
    distance_threshold: float,
    estimation_method: reg.TransformationEstimation = reg.TransformationEstimationForColoredICP(),
    convergence_criteria: reg.ICPConvergenceCriteria = reg.ICPConvergenceCriteria(),
) -> RegistrationResult:
    """Registers the source to the target with ICP."""

    result: reg.RegistrationResult = reg.registration_colored_icp(
        source=source,
        target=target,
        init=transformation,
        max_correspondence_distance=distance_threshold,
        estimation_method=estimation_method,
        criteria=convergence_criteria,
    )

    information: np.ndarray = reg.get_information_matrix_from_point_clouds(
        source=source,
        target=target,
        max_correspondence_distance=distance_threshold,
        transformation=result.transformation,
    )

    return RegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=result.correspondence_set,
        transformation=result.transformation,
        information=information,
    )


def build_pose_graph(
    results: dict[int, dict[int, RegistrationResult]],
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
