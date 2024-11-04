"""Module for incremental point cloud registrators."""

import numpy as np
import open3d.pipelines.registration as reg

from mynd.geometry import PointCloud
from mynd.utils.result import Result

from .data_types import RegistrationResult
from .processor_types import IncrementalRegistrator


def register_regular_icp(
    source: PointCloud,
    target: PointCloud,
    transformation: np.ndarray,
    *,
    distance_threshold: float,
    estimation_method: reg.TransformationEstimation = reg.TransformationEstimationPointToPlane(),
    convergence_criteria: reg.ICPConvergenceCriteria = reg.ICPConvergenceCriteria(),
) -> RegistrationResult:
    """Registers the source to the target with ICP."""

    result: reg.RegistrationResult = reg.registration_icp(
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
    max_iteration: int = 30,
    relative_fitness: float = 1e-06,
    relative_rmse: float = 1e-06,
) -> reg.ICPConvergenceCriteria:
    """Creates a ICP convergence criteria."""
    return reg.ICPConvergenceCriteria(
        max_iteration=max_iteration,
        relative_fitness=relative_fitness,
        relative_rmse=relative_rmse,
    )


def create_point_to_plane_estimator(
    kernel: reg.RobustKernel | None = None,
) -> reg.TransformationEstimation:
    """Creates a point to plane transformation estimator."""
    return reg.TransformationEstimationPointToPlane(kernel=kernel)


def create_generalized_icp_estimator(
    epsilon: float,
    kernel: reg.RobustKernel | None = None,
) -> reg.TransformationEstimation:
    """Creates a generalized ICP transformation estimator."""
    return reg.TransformationEstimationForGeneralizedICP(
        epsilon=epsilon, kernel=kernel
    )


def create_colored_icp_estimator(
    lambda_geometric: float,
    kernel: reg.RobustKernel | None = None,
) -> reg.TransformationEstimation:
    """Creates a colored ICP transformation estimator."""
    return reg.TransformationEstimationForColoredICP(
        lambda_geometric=lambda_geometric,
        kernel=kernel,
    )


def create_regular_icp_registrator(
    estimation_method: reg.TransformationEstimation,
    convergence_criteria: reg.ICPConvergenceCriteria,
    distance_threshold: float,
) -> IncrementalRegistrator:
    """Creates a regular ICP registrator from the given arguments."""

    def regular_icp_wrapper(
        source: PointCloud,
        target: PointCloud,
        transformation: np.ndarray,
    ) -> RegistrationResult:
        """Closure wrapper for regular ICP registration method."""
        return register_regular_icp(
            source=source,
            target=target,
            transformation=transformation,
            estimation_method=estimation_method,
            convergence_criteria=convergence_criteria,
            distance_threshold=distance_threshold,
        )

    return regular_icp_wrapper


def create_colored_icp_registrator(
    estimation_method: reg.TransformationEstimation,
    convergence_criteria: reg.ICPConvergenceCriteria,
    distance_threshold: float,
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
            distance_threshold=distance_threshold,
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


# TODO: Add named tuple to hold build keys
BUILD_HUBER_KEY: str = "huber_kernel"
BUILD_TUKEY_KEY: str = "tukey_kernel"
CONVERGENCE_CRITERIA_KEY: str = "convergence_criteria"
DISTANCE_THRESHOLD_KEY: str = "distance_threshold"


def build_regular_icp_registrator(
    parameters: dict,
) -> Result[IncrementalRegistrator, str]:
    """Builds a regular ICP registrator from a configuration."""

    if BUILD_HUBER_KEY in parameters:
        kernel: reg.RobustKernel = create_huber_loss(
            **parameters.get(BUILD_HUBER_KEY)
        )
    elif BUILD_TUKEY_KEY in parameters:
        kernel: reg.RobustKernel = create_tukey_loss(
            **parameters.get(BUILD_TUKEY_KEY)
        )
    else:
        kernel = None

    # NOTE: For now we only use a point to plane estimator for regular ICP
    estimator: reg.TransformationEstimation = create_point_to_plane_estimator(
        kernel=kernel
    )

    if CONVERGENCE_CRITERIA_KEY in parameters:
        convergence_criteria: reg.ICPConvergenceCriteria = (
            create_icp_convergence_criteria(
                **parameters.get(CONVERGENCE_CRITERIA_KEY)
            )
        )
    else:
        convergence_criteria: reg.ICPConvergenceCriteria = (
            create_icp_convergence_criteria()
        )

    if DISTANCE_THRESHOLD_KEY not in parameters:
        raise ValueError(
            f"regular icp builder: missing key '{DISTANCE_THRESHOLD_KEY}'"
        )

    distance_threshold: float = parameters.get("distance_threshold")

    return create_regular_icp_registrator(
        estimation_method=estimator,
        convergence_criteria=convergence_criteria,
        distance_threshold=distance_threshold,
    )


def build_colored_icp_registrator(
    parameters: dict,
) -> IncrementalRegistrator:
    """Builds an incremental registrator from a configuration."""

    COLOR_ESTIMATOR_KEY: str = "colored_icp_estimation"

    if BUILD_HUBER_KEY in parameters:
        kernel: reg.RobustKernel = create_huber_loss(
            **parameters.get(BUILD_HUBER_KEY)
        )
    elif BUILD_TUKEY_KEY in parameters:
        kernel: reg.RobustKernel = create_tukey_loss(
            **parameters.get(BUILD_TUKEY_KEY)
        )
    else:
        kernel = None

    if COLOR_ESTIMATOR_KEY in parameters:
        estimator: reg.TransformationEstimation = create_colored_icp_estimator(
            **parameters.get(COLOR_ESTIMATOR_KEY),
            kernel=kernel,
        )
    else:
        raise ValueError(
            f"colored icp builder: missing key '{COLOR_ESTIMATOR_KEY}'"
        )

    if CONVERGENCE_CRITERIA_KEY in parameters:
        criteria: reg.ICPConvergenceCriteria = create_icp_convergence_criteria(
            **parameters.get(CONVERGENCE_CRITERIA_KEY),
        )

    if DISTANCE_THRESHOLD_KEY not in parameters:
        raise ValueError(
            f"colored icp builder: missing key '{DISTANCE_THRESHOLD_KEY}'"
        )

    distance_threshold: float = parameters.get(DISTANCE_THRESHOLD_KEY)

    return create_colored_icp_registrator(
        estimation_method=estimator,
        convergence_criteria=criteria,
        distance_threshold=distance_threshold,
    )
