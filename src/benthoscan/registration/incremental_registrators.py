"""Module for incremental point cloud registrators."""

from typing import Any, Optional

import numpy as np
import open3d.pipelines.registration as reg

from .data_types import PointCloud, RegistrationResult
from .processor_types import IncrementalRegistrator


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


"""
ICP registration factories:
 - create_icp_convergence_criteria
 - create_generalized_icp_estimator
 - create_colored_icp_estimator
 - create_regular_icp_registrator
 - create_colored_icp_registrator
"""


def create_icp_convergence_criteria(
    max_iteration: int,
    relative_fitness: float,
    relative_rmse: float,
) -> reg.ICPConvergenceCriteria:
    """Creates a ICP convergence criteria."""
    return reg.ICPConvergenceCriteria(
        max_iteration=max_iteration,
        relative_fitness=relative_fitness,
        relative_rmse=relative_rmse,
    )


def create_generalized_icp_estimator(
    epsilon: float,
    kernel: Optional[reg.RobustKernel] = None,
) -> reg.TransformationEstimation:
    """Creates a generalized ICP transformation estimator."""
    return reg.TransformationEstimationForGeneralizedICP(epsilon=epsilon, kernel=kernel)


def create_colored_icp_estimator(
    lambda_geometric: float,
    kernel: Optional[reg.RobustKernel] = None,
) -> reg.TransformationEstimation:
    """Creates a colored ICP transformation estimator."""
    return reg.TransformationEstimationForColoredICP(
        lambda_geometric=lambda_geometric,
        kernel=kernel,
    )


def create_regular_icp_registrator(
    estimation_method: reg.TransformationEstimation,
    convergence_criteria: reg.ICPConvergenceCriteria,
    parameters: dict[str, Any],
) -> IncrementalRegistrator:
    """Creates a regular ICP registrator from the given arguments."""

    def regular_icp_wrapper(
        source: PointCloud,
        target: PointCloud,
        transformation: np.ndarray,
    ) -> RegistrationResult:
        """Closure wrapper for regular ICP registration method."""
        return register_icp(
            source=source,
            target=target,
            transformation=transformation,
            estimation_method=estimation_method,
            convergence_criteria=convergence_criteria,
            **parameters,
        )

    return regular_icp_wrapper


def create_colored_icp_registrator(
    estimation_method: reg.TransformationEstimation,
    convergence_criteria: reg.ICPConvergenceCriteria,
    parameters: dict[str, Any],
) -> IncrementalRegistrator:
    """Creates a colored ICP registrator from the given arguments."""

    def colored_icp_wrapper(
        source: PointCloud,
        target: PointCloud,
        transformation: np.ndarray,
    ) -> RegistrationResult:
        """Closure wrapper for colored ICP registration method."""
        return register_colored_icp(
            source=source,
            target=target,
            transformation=transformation,
            estimation_method=estimation_method,
            convergence_criteria=convergence_criteria,
            **parameters,
        )

    return colored_icp_wrapper


"""
Robust kernel factories:
 - create_huber_loss
 - create_tukey_loss
"""


def create_huber_loss(k: float) -> reg.RobustKernel:
    """Creates a robust kernel with Huber loss."""
    return reg.HuberLoss(k=k)


def create_tukey_loss(k: float) -> reg.RobustKernel:
    """Creates a robust kernel with Tukey loss."""
    return reg.TukeyLoss(k=k)


# TODO: Move full registrator functionality to separate module

"""
Full registration functionality:
 - build_pose_graph
 - optimize_pose_graph
"""


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
