"""Module for point cloud processors, i.e. including filters for spacing and confidence."""

import functools
import copy

from typing import Any

import open3d.geometry as geom
import open3d.pipelines.registration as reg

# NOTE: Some report memory bugs if numpy is import before open3d
import numpy as np

from mynd.geometry import PointCloud

from .data_types import Feature, RegistrationResult

from .processor_types import (
    FeatureExtractor,
    FeatureRegistrator,
    GlobalRegistrator,
)


def extract_fpfh_features(
    input: PointCloud, radius: float, neighbours: int
) -> Feature:
    """Compute fast point feature histrograms (FPFH)"""
    return reg.compute_fpfh_feature(
        input=input,
        search_param=geom.KDTreeSearchParamHybrid(
            radius=radius,
            max_nn=neighbours,
        ),
    )


def extract_features_and_register(
    source: PointCloud,
    target: PointCloud,
    feature_extractor: FeatureExtractor,
    feature_registrator: FeatureRegistrator,
) -> RegistrationResult:
    """Executor for feature-based registration methods."""

    source_features: Feature = feature_extractor(input=source)
    target_features: Feature = feature_extractor(input=target)

    result: RegistrationResult = feature_registrator(
        source=source,
        target=target,
        source_features=source_features,
        target_features=target_features,
    )

    return result


def generate_correspondence_validators(
    distance_threshold: float,
    edge_threshold: float | None = None,
    normal_threshold: float | None = None,
) -> list[reg.CorrespondenceChecker]:
    """Generates a set of correspondence validators."""

    validators: list = [
        reg.CorrespondenceCheckerBasedOnDistance(distance_threshold)
    ]

    if edge_threshold:
        validators.append(
            reg.CorrespondenceCheckerBasedOnEdgeLength(edge_threshold)
        )
    if edge_threshold:
        validators.append(
            reg.CorrespondenceCheckerBasedOnNormal(normal_threshold)
        )

    return validators


def match_fast_wrapper(
    source: PointCloud,
    target: PointCloud,
    source_features: Feature,
    target_features: Feature,
    distance_threshold: float,
) -> RegistrationResult:
    """Wrapper function for Open3D feature based FAST registration method."""

    option: reg.FastGlobalRegistrationOption = reg.FastGlobalRegistrationOption(
        maximum_correspondence_distance=distance_threshold,
    )

    result: reg.RegistrationResult = (
        reg.registration_fgr_based_on_feature_matching(
            source=source,
            target=target,
            source_feature=source_features,
            target_feature=target_features,
            option=option,
        )
    )

    information_matrix: np.ndarray = (
        reg.get_information_matrix_from_point_clouds(
            source=source,
            target=target,
            max_correspondence_distance=distance_threshold,
            transformation=result.transformation,
        )
    )

    return RegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=np.asarray(result.correspondence_set),
        transformation=result.transformation,
        information=information_matrix,
    )


def register_features_fast(
    source: PointCloud,
    target: PointCloud,
    feature_extractor: FeatureExtractor,
    distance_threshold: float,
) -> RegistrationResult:
    """Extracts features and performs registration with FAST matching."""

    # TODO: Add wrapper around Open3D function + information matrix estimation
    feature_registrator: FeatureRegistrator = functools.partial(
        match_fast_wrapper,
        distance_threshold=distance_threshold,
    )

    return extract_features_and_register(
        source=source,
        target=target,
        feature_extractor=feature_extractor,
        feature_registrator=feature_registrator,
    )


def match_features_ransac(
    source: PointCloud,
    target: PointCloud,
    source_features: Feature,
    target_features: Feature,
    estimation_method: reg.TransformationEstimation,
    validators: list[reg.CorrespondenceChecker],
    convergence_criteria: reg.RANSACConvergenceCriteria,
    distance_threshold: float,
    sample_count: int = 3,
    mutual_filter: bool = True,
) -> RegistrationResult:
    """Wrapper function for Open3D feature based RANSAC registration method."""

    result: reg.RegistrationResult = (
        reg.registration_ransac_based_on_feature_matching(
            source=source,
            target=target,
            source_feature=source_features,
            target_feature=target_features,
            max_correspondence_distance=distance_threshold,
            mutual_filter=mutual_filter,
            ransac_n=sample_count,
            estimation_method=estimation_method,
            checkers=validators,
            criteria=convergence_criteria,
        )
    )

    information_matrix: np.ndarray = (
        reg.get_information_matrix_from_point_clouds(
            source=source,
            target=target,
            max_correspondence_distance=distance_threshold,
            transformation=result.transformation,
        )
    )

    return RegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=np.asarray(result.correspondence_set),
        transformation=result.transformation,
        information=information_matrix,
    )


def register_features_ransac(
    source: PointCloud,
    target: PointCloud,
    feature_extractor: FeatureExtractor,
    estimation_method: reg.TransformationEstimation,
    validators: list[reg.CorrespondenceChecker],
    convergence_criteria: reg.RANSACConvergenceCriteria,
    distance_threshold: float,
    sample_count: int = 3,
    mutual_filter: bool = True,
) -> RegistrationResult:
    """Extracts features and performs registration with RANSAC matching."""

    source: PointCloud = copy.deepcopy(source)
    target: PointCloud = copy.deepcopy(target)

    source_features: Feature = feature_extractor(input=source)
    target_features: Feature = feature_extractor(input=target)

    return match_features_ransac(
        source=source,
        target=target,
        source_features=source_features,
        target_features=target_features,
        estimation_method=estimation_method,
        validators=validators,
        convergence_criteria=convergence_criteria,
        distance_threshold=distance_threshold,
        sample_count=sample_count,
        mutual_filter=mutual_filter,
    )


"""
Factories functions:
 - create_fpfh_extractor
 - create_ransac_convergence_criteria
 - create_ransac_registrator
 - create_point_to_point_estimator
 - create_point_to_plane_estimator
"""


def create_fpfh_extractor(radius: float, neighbours: int) -> FeatureExtractor:
    """Creates a FPFH feature extractor."""

    def feature_extractor_wrapper(input: PointCloud) -> Feature:
        return extract_fpfh_features(
            input=input, radius=radius, neighbours=neighbours
        )

    return feature_extractor_wrapper


def create_ransac_convergence_criteria(
    max_iteration: int,
    confidence: float,
) -> reg.RANSACConvergenceCriteria:
    """Creates a RANSAC convergence convergence criteria."""
    return reg.RANSACConvergenceCriteria(
        max_iteration=max_iteration, confidence=confidence
    )


def create_ransac_registrator(
    feature_extractor: FeatureExtractor,
    estimation_method: reg.TransformationEstimation,
    validators: list[reg.CorrespondenceChecker],
    convergence_criteria: reg.RANSACConvergenceCriteria,
    distance_threshold: float,
    sample_count: int = 3,
    mutual_filter: bool = True,
) -> GlobalRegistrator:
    """Creates a wrapper around a RANSAC registrator."""

    def ransac_registrator_wrapper(
        source: PointCloud,
        target: PointCloud,
    ) -> RegistrationResult:
        """Wraps RANSAC registration method."""

        return register_features_ransac(
            source,
            target,
            feature_extractor=feature_extractor,
            estimation_method=estimation_method,
            validators=validators,
            convergence_criteria=convergence_criteria,
            distance_threshold=distance_threshold,
            sample_count=sample_count,
            mutual_filter=mutual_filter,
        )

    return ransac_registrator_wrapper


def create_point_to_point_estimator(
    with_scaling: bool = False,
) -> reg.TransformationEstimation:
    """Creates a point to point transformation estimator."""
    return reg.TransformationEstimationPointToPoint(with_scaling=with_scaling)


def create_point_to_plane_estimator(
    kernel: reg.RobustKernel | None = None,
) -> reg.TransformationEstimation:
    """Creates a point to plane transformation estimator."""
    return reg.TransformationEstimationPointToPlane(kernel=kernel)


def build_ransac_registrator(components: dict[str, Any]) -> GlobalRegistrator:
    """Builds a RANSAC registrator from a collection of parameters."""

    for key in [
        "feature",
        "estimator",
        "validators",
        "convergence",
        "algorithm",
    ]:
        assert key in components, f"missing build component: {key}"

    feature_extractor: FeatureExtractor = create_fpfh_extractor(
        **components.get("feature")
    )
    estimation_method = create_point_to_point_estimator(
        **components.get("estimator")
    )
    validators = generate_correspondence_validators(
        **components.get("validators")
    )
    convergence_criteria = create_ransac_convergence_criteria(
        **components.get("convergence")
    )

    return create_ransac_registrator(
        feature_extractor=feature_extractor,
        estimation_method=estimation_method,
        validators=validators,
        convergence_criteria=convergence_criteria,
        **components.get("algorithm"),
    )
