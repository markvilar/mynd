"""Module for point cloud processors, i.e. including filters for spacing and confidence."""

from copy import deepcopy
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import open3d

import open3d.geometry as geom
import open3d.pipelines.registration as regi
import open3d.utility as util

from benthoscan.utils.log import logger

from .point_cloud_types import PointCloud
from .point_cloud_loaders import PointCloudLoader


def downsample_point_cloud(
    cloud: PointCloud,
    spacing: float,
    inplace: bool = False,
) -> PointCloud:
    """Downsamples a point cloud by performing voxel resampling."""
    if not inplace:
        cloud = deepcopy(cloud)

    cloud = cloud.voxel_down_sample(voxel_size=spacing)
    return cloud


def estimate_point_cloud_normals(
    cloud: PointCloud,
    radius: float = 0.1,
    neighbours: int = 30,
    inplace: bool = False,
) -> PointCloud:
    """Estimates the normals of a point cloud based on neighbouring points."""
    if not inplace:
        cloud = deepcopy(cloud)

    cloud.estimate_normals(
        search_param=geom.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
    )
    return cloud


@dataclass
class ExtendedRegistrationResult:
    """Class representing registration results in addition to the information matrix."""

    fitness: float
    inlier_rmse: float
    correspondence_set: np.ndarray
    transformation: np.ndarray
    information: np.ndarray


Transformation = np.ndarray

GlobalRegistrator = Callable[[PointCloud, PointCloud], ExtendedRegistrationResult]
IncrementalRegistrator = Callable[
    [PointCloud, PointCloud, Transformation], ExtendedRegistrationResult
]

FullRegistrator = Callable[[list[PointCloud]], list[ExtendedRegistrationResult]]


def register_point_cloud_fphp_fast(
    source: PointCloud,
    target: PointCloud,
    distance_threshold: float,
    feature_radius: float = 1.50,
    feature_neighbours: int = 300,
) -> ExtendedRegistrationResult:
    """Registers the source to the target based on fast FPFH matching."""

    feature_extractor = partial(
        regi.compute_fpfh_feature,
        search_param=geom.KDTreeSearchParamHybrid(
            radius=feature_radius, max_nn=feature_neighbours
        ),
    )

    source_features: regi.Feature = feature_extractor(input=source)
    target_features: regi.Feature = feature_extractor(input=target)

    options: regi.FastGlobalRegistrationOption = regi.FastGlobalRegistrationOption(
        maximum_correspondence_distance=distance_threshold,
    )

    result: regi.RegistrationResult = regi.registration_fgr_based_on_feature_matching(
        source=source,
        target=target,
        source_feature=source_features,
        target_feature=target_features,
        option=options,
    )

    information: np.ndarray = regi.get_information_matrix_from_point_clouds(
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
    sample_count: int = 4,
    max_iterations: int = 50000,
    confidence: float = 0.999,
    edge_check: Optional[float] = None,
    normal_check: Optional[float] = None,
) -> ExtendedRegistrationResult:
    """Registers the source to the target based on FPFH matching."""

    feature_extractor = partial(
        regi.compute_fpfh_feature,
        search_param=geom.KDTreeSearchParamHybrid(
            radius=feature_radius, max_nn=feature_neighbours
        ),
    )

    source_features: regi.Feature = feature_extractor(input=source)
    target_features: regi.Feature = feature_extractor(input=target)

    ESTIMATOR: regi.TransformationEstimation = (
        regi.TransformationEstimationPointToPoint(with_scaling=True)
    )

    checkers: list[CorrespondenceChecker] = [
        regi.CorrespondenceCheckerBasedOnDistance(distance_threshold),
    ]

    if edge_check:
        checkers.append(regi.CorrespondenceCheckerBasedOnEdgeLength(edge_check))
    if normal_check:
        checkers.append(regi.CorrespondenceCheckerBasedOnNormal(normal_check))

    CONVERGENCE = regi.RANSACConvergenceCriteria(
        max_iteration=max_iterations,
        confidence=confidence,
    )

    result: regi.RegistrationResult = (
        regi.registration_ransac_based_on_feature_matching(
            source=source,
            target=target,
            source_feature=source_features,
            target_feature=target_features,
            max_correspondence_distance=distance_threshold,
            mutual_filter=True,
            estimation_method=ESTIMATOR,
            ransac_n=sample_count,
            checkers=CHECKERS,
            criteria=CONVERGENCE,
        )
    )

    information = regi.get_information_matrix_from_point_clouds(
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
    distance_measure: regi.TransformationEstimation = regi.TransformationEstimationPointToPlane(),
) -> ExtendedRegistrationResult:
    """Registers the source to the target with ICP."""

    if not source.has_normals():
        return Err("source point cloud does not have normals")

    if not target.has_normals():
        return Err("target point cloud does not have normals")

    result: regi.RegistrationResult = regi.registration_icp(
        source,
        target,
        distance_threshold,
        transformation,
        distance_measure,
    )

    information = regi.get_information_matrix_from_point_clouds(
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


@dataclass
class MultiTargetIndex:
    source: int
    targets: list[int]


def generate_cascade_indices(count: int) -> list[MultiTargetIndex]:
    """Generates a list of cascaded multi-target indices."""

    sources: list[int] = list(range(count))

    indices: list[MultiTargetIndex] = list()
    for source in sources:
        targets: list[int] = list(range(source + 1, count))
        indices.append(MultiTargetIndex(source, targets))

    return indices


PairRegistrator = Callable[[PointCloud, PointCloud], ExtendedRegistrationResult]


def register_point_cloud_pair(
    source: PointCloud,
    target: PointCloud,
    global_registrator: GlobalRegistrator,
    incremental_registrator: IncrementalRegistrator,
) -> ExtendedRegistrationResult:
    """Registers a pair of point clouds with global and iterative registrators."""

    global_result: ExtendedRegistrationResult = global_registrator(
        source=source,
        target=target,
    )

    incremental_result: ExtendedRegistrationResult = incremental_registrator(
        source=source,
        target=target,
        transformation=global_result.transformation,
    )

    return incremental_result


def build_registration_pose_graph(
    loaders: list[PointCloudLoader],
    pair_registrator: PairRegistrator,
    indices: list[MultiTargetIndex],
) -> regi.PoseGraph:
    """Builds a pose graph for point cloud registration with pair-wise
    registrations as initial transformations."""
    odometry = np.identity(4)

    pose_graph = regi.PoseGraph()
    pose_graph.nodes.append(regi.PoseGraphNode(odometry))

    for index in indices:
        source_id: int = index.source
        source_cloud: PointCloud = loaders[source_id]().unwrap()

        for target_id in index.target:
            target_cloud: PointCloud = loaders[target_id]().unwrap()

            results: ExtendedRegistrationResult = pair_registrator(
                source_cloud,
                target_cloud,
            )

            if target_id == source_id + 1:  # odometry case
                odometry = np.dot(transformation, odometry)
                pose_graph.nodes.append(
                    regi.PoseGraphNode(
                        np.linalg.inv(odometry),
                    )
                )
                pose_graph.edges.append(
                    regi.PoseGraphEdge(
                        source_id,
                        target_id,
                        results.transformation,
                        results.information,
                        uncertain=False,
                    )
                )
            else:  # loop closure case
                pose_graph.edges.append(
                    regi.PoseGraphEdge(
                        source_id,
                        target_id,
                        results.transformation,
                        results.information,
                        uncertain=True,
                    )
                )

    return pose_graph


def register_point_cloud_graph(
    loaders: list[PointCloudLoader],
    pair_registrator: PairRegistrator,
    correspondence_distance: float,
    prune_distance: float,
    indices: list[MultiTargetIndex] = None,
) -> regi.PoseGraph:
    """Performs full registration of a collection of point clouds."""

    if not indices:
        indices: list[MultiTargetIndex] = generate_cascade_indices(len(loaders))

    pose_graph: regi.PoseGraph = build_registration_pose_graph(
        loaders,
        pair_registrator,
        indices,
    )

    option = regi.GlobalOptimizationOption(
        max_correspondence_distance=correspondence_distance,
        edge_prune_threshold=prune_distance,
        reference_node=0,
    )

    with util.VerbosityContextManager(util.VerbosityLevel.Debug) as cm:
        regi.global_optimization(
            pose_graph,
            regi.GlobalOptimizationLevenbergMarquardt(),
            regi.GlobalOptimizationConvergenceCriteria(),
            option,
        )

    return pose_graph
