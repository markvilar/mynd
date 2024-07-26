"""Module for building point cloud registrators."""

import inspect

from dataclasses import dataclass
from collections.abc import Callable
from functools import partial
from typing import Any, Optional

from result import Ok, Err, Result

import open3d.pipelines.registration as reg

from benthoscan.utils.log import logger

from .feature_registrators import (
    extract_fpfh_features,
    extract_features_and_register,
    generate_correspondence_validators,
    register_features_fast,
    register_features_ransac,
)
from .incremental_registrators import (
    register_icp,
    register_colored_icp,
)
from .point_cloud_processors import (
    downsample_point_cloud,
    estimate_point_cloud_normals,
)
from .processor_types import (
    PointCloudProcessor,
    FeatureExtractor,
    FeatureRegistrator,
    GlobalRegistrator,
    IncrementalRegistrator,
)


FEATURE_REGISTRATOR_ALGORITHMS = ["feature_matching_ransac"]
ICP_REGISTRATOR_ALGORITHMS = ["icp", "colored_icp", "generalized_icp"]


def create_fpfh_extractor(radius: float, neighbours: int) -> FeatureExtractor:
    """Creates a FPFH feature extractor."""
    return partial(extract_fpfh_features, radius=radius, neighbours=neighbours)


def create_huber_loss(k: float) -> reg.RobustKernel:
    """Creates a robust kernel with Huber loss."""
    return reg.HuberLoss(k=k)


def create_tukey_loss(k: float) -> reg.RobustKernel:
    """Creates a robust kernel with Tukey loss."""
    return reg.TukeyLoss(k=k)


def create_ransac_convergence_criteria(
    max_iteration: int,
    confidence: float,
) -> reg.RANSACConvergenceCriteria:
    """Creates a RANSAC convergence convergence_criteria."""
    return reg.RANSACConvergenceCriteria(
        max_iteration=max_iteration, confidence=confidence
    )


def create_icp_convergence_criteria(
    max_iteration: int,
    relative_fitness: float,
    relative_rmse: float,
) -> reg.ICPConvergenceCriteria:
    """Creates a ICP convergence convergence_criteria."""
    return reg.ICPConvergenceCriteria(
        max_iteration=max_iteration,
        relative_fitness=relative_fitness,
        relative_rmse=relative_rmse,
    )


def create_point_to_point_estimator(
    with_scaling: bool = False,
) -> reg.TransformationEstimation:
    """Creates a point to point transformation estimator."""
    return reg.TransformationEstimationPointToPoint(with_scaling=with_scaling)


def create_point_to_plane_estimator(
    kernel: Optional[reg.RobustKernel] = None,
) -> reg.TransformationEstimation:
    """Creates a point to plane transformation estimator."""
    return reg.TransformationEstimationPointToPlane(kernel=kernel)


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


@dataclass
class ComponentBuildData:
    """Class representing build data for a component."""

    factory: Callable
    parameters: dict[str, Any]


ComponentBuildResult = Result[ComponentBuildData, str]


def validate_build_component(build_data: ComponentBuildData) -> Result[None, str]:
    """TODO"""

    signature: inspect.Signature = inspect.signature(build_data.factory)

    required_parameters: list[str] = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect.Parameter.empty
    ]

    # Check the provided parameters are valid parameters
    for parameter in build_data.parameters:
        if parameter in signature.parameters:
            continue

        message: str = f"invalid component parameter: {parameter}"
        logger.info(build_data.factory.__name__)
        logger.info(message)
        return Err(message)

    # Check required parameters
    for parameter in required_parameters:
        if parameter in build_data.parameters:
            continue

        message: str = f"missing required parameter: {parameter}"
        logger.info(build_data.factory.__name__)
        logger.info(message)
        return Err(message)

    return Ok(None)


def build_and_validate_component(
    type_flag: str,
    parameters: dict[str, Any],
    build_fun: Callable,
) -> ComponentBuildResult:
    """Setup component and validate."""

    build_result: ComponentBuildResult = build_fun(
        type_flag=type_flag, parameters=parameters
    )

    if build_result.is_err():
        return build_result

    build_data: ComponentBuildData = build_result.ok()

    validation_result: Result[None, str] = validate_build_component(build_data)
    match validation_result:
        case Ok():
            return Ok(build_data)
        case Err(message):
            return Err(message)
        case other:
            return Err("unknown component build error")


def build_point_cloud_processor(
    method: str,
    keywords: dict[str, Any],
) -> Result[PointCloudProcessor, str]:
    """Builds a point cloud preprocessor from a configuration."""

    match method:
        case "downsample":
            processor: PointCloudProcessor = partial(
                downsample_point_cloud,
                **keywords,
            )
            return Ok(processor)
        case "estimate_normals":
            processor: PointCloudProcessor = partial(
                estimate_point_cloud_normals,
                **keywords,
            )
            return Ok(processor)
        case other:
            return Err(f"invalid point cloud processor: {method}")


@dataclass
class FeatureRegistratorBuildState:
    """Class representing a feature registrator build state."""

    kernel: ComponentBuildData = None
    feature_extractor: ComponentBuildData = None
    estimation_method: ComponentBuildData = None
    validators: ComponentBuildData = None
    convergence_criteria: ComponentBuildData = None


FeatureRegistratorBuildResult = Result[FeatureRegistratorBuildState, str]


def add_feature_extractor(
    type_flag: str,
    parameters: dict[str, Any],
) -> ComponentBuildResult:
    """Creates a feature extractor from a configuration and adds it to the build state
    of a feature-based registrator."""

    match type_flag:
        case "fpfh":
            factory: Callable = create_fpfh_extractor
        case other:
            return Err(f"invalid feature extractor type: {type_flag}")

    return Ok(ComponentBuildData(factory=factory, parameters=parameters))


def add_feature_estimation_method(
    type_flag: str,
    parameters: dict[str, Any],
) -> ComponentBuildResult:
    """Creates a factory for a feature estimation method and adds it to the build state."""

    match type_flag:
        case "point_to_point":
            factory: Callable = create_point_to_point_estimator
        case "point_to_plane":
            factory: Callable = create_point_to_plane_estimator
        case other:
            return Err(f"invalid feature estimation method: {type_flag}")

    return Ok(ComponentBuildData(factory=factory, parameters=parameters))


def add_feature_validators(
    type_flag: str,
    parameters: dict[str, Any],
) -> ComponentBuildResult:
    """Creates a factory for correspondence validators and adds it to the build state."""

    match type_flag:
        case "correspondence_validators":
            factory: Callable = generate_correspondence_validators
        case other:
            return Err(f"invalid feature validator: {type_flag}")

    return Ok(ComponentBuildData(factory=factory, parameters=parameters))


def add_feature_convergence_criteria(
    type_flag: str,
    parameters: dict[str, Any],
) -> ComponentBuildResult:
    """Creates a factory for convergence convergence_criteria and adds it to the build state."""

    match type_flag:
        case "ransac_convergence_criteria":
            factory: Callable = create_ransac_convergence_criteria
        case other:
            return Err(f"invalid convergence convergence_criteria: {type_flag}")

    return Ok(ComponentBuildData(factory=factory, parameters=parameters))


def compile_feature_registrator(
    build_state: FeatureRegistratorBuildState,
    algorithm: str,
    parameters: dict[str, Any],
) -> Result[GlobalRegistrator, str]:
    """Compiles a feature registrator based on the given build state."""

    try:
        extractor = build_state.feature_extractor.factory(
            **build_state.feature_extractor.parameters
        )
        estimation_method = build_state.estimation_method.factory(
            **build_state.estimation_method.parameters
        )
        validators = build_state.validators.factory(**build_state.validators.parameters)
        convergence_criteria = build_state.convergence_criteria.factory(
            **build_state.convergence_criteria.parameters
        )
    except TypeError as error:
        return Err(str(error))

    match algorithm:
        case "feature_matching_ransac":
            registrator: FeatureRegistrator = partial(
                register_features_ransac,
                **parameters,
                feature_extractor=extractor,
                estimation_method=estimation_method,
                validators=validators,
                convergence_criteria=convergence_criteria,
            )
            return Ok(registrator)
        case other:
            return Err("invalid feature registration algorithm: {algorithm}")


def build_feature_registrator(config: dict) -> Result[GlobalRegistrator, str]:
    """Builds a registration process, i.e. preprocessors and registrator, from a
    configuration."""

    components: dict[str, str] = config.get("component_types", dict())
    parameters: dict[str, dict] = config.get("component_parameters", dict())

    if not components:
        return Err(f"invalid configuration: missing key 'component_types'")
    if not parameters:
        return Err(f"invalid configuration: missing key 'component_parameters'")

    build_funs: dict[str, Callable] = {
        "feature_extractor": add_feature_extractor,
        "estimation_method": add_feature_estimation_method,
        "validators": add_feature_validators,
        "convergence_criteria": add_feature_convergence_criteria,
    }

    build_results: dict[str, ComponentBuildResult] = {
        key: build_and_validate_component(
            type_flag=components.get(key, None),
            parameters=parameters.get(key, dict()),
            build_fun=build_fun,
        )
        for key, build_fun in build_funs.items()
    }

    components: dict[str, ComponentBuildData] = dict()
    for key, build_result in build_results.items():
        match build_result:
            case Ok(component_data):
                components[key] = component_data
            case Err(message):
                return build_result

    state: FeatureRegistratorBuildState = FeatureRegistratorBuildState(**components)

    return compile_feature_registrator(
        build_state=state,
        algorithm=config.get("algorithm"),
        parameters=config.get("parameters"),
    )


@dataclass
class ICPBuildState:
    """Class representing a ICP build state."""

    kernel: ComponentBuildData = None
    estimation_method: ComponentBuildData = None
    convergence_criteria: ComponentBuildData = None


ICPBuildResult = Result[ICPBuildState, str]


def add_icp_robust_kernel(
    type_flag: str,
    parameters: dict = dict(),
) -> ICPBuildResult:
    """Creates a robust kernel from a configuration and adds it to the build state."""

    match type_flag:
        case "huber":
            factory: Callable = create_huber_loss
        case "tukey":
            factory: Callable = create_tukey_loss
        case other:
            return Err(f"invalid ICP robust kernel: {type_flag}")

    return Ok(ComponentBuildData(factory=factory, parameters=parameters))


def add_icp_estimation_method(
    type_flag: str,
    parameters: dict = dict(),
) -> ICPBuildResult:
    """Creates a transformation estimation method from a configuration and adds it to the current
    build state."""

    match type_flag:
        case "point_to_point":
            factory: Callable = create_point_to_point_estimator
        case "point_to_plane":
            factory: Callable = create_point_to_plane_estimator
        case "generalized_icp":
            factory: Callable = create_generalized_icp_estimator
        case "colored_icp":
            factory: Callable = create_colored_icp_estimator
        case other:
            return Err(f"invalid ICP estimation method: {type_flag}")

    return Ok(ComponentBuildData(factory=factory, parameters=parameters))


def add_icp_convergence_criteria(
    type_flag: str,
    parameters: dict = dict(),
) -> ICPBuildResult:
    """Creates component build data for an ICP convergence convergence_criteria."""

    factory: Callable = create_icp_convergence_criteria

    return Ok(ComponentBuildData(factory=factory, parameters=parameters))


def compile_icp_registrator(
    build_state: ICPBuildState,
    algorithm: str,
    parameters: dict[str, Any],
) -> Result[IncrementalRegistrator, None]:
    """Sets up an ICP callable with the given parameters."""

    if not build_state.estimation_method:
        return Err(f"missing ICP estimation method")
    if not build_state.convergence_criteria:
        return Err(f"missing ICP convergence convergence_criteria")

    try:
        if build_state.kernel:
            kernel = build_state.kernel.factory(**build_state.kernel.parameters)
            estimation_method = build_state.estimation_method.factory(
                kernel=kernel, **build_state.estimation_method.parameters
            )
        else:
            estimation_method = build_state.estimation_method.factory(
                **build_state.estimation_method.parameters
            )

        convergence_criteria = build_state.convergence_criteria.factory(
            **build_state.convergence_criteria.parameters
        )
    except TypeError as error:
        return Err(f"invalid ICP configuration: {error}")

    match algorithm:
        case "icp":
            registrator = partial(
                register_icp,
                **parameters,
                estimation_method=estimation_method,
                convergence_criteria=convergence_criteria,
            )
            return Ok(registrator)
        case "colored_icp":
            registrator = partial(
                register_colored_icp,
                **parameters,
                estimation_method=estimation_method,
                convergence_criteria=convergence_criteria,
            )
            return Ok(registrator)
        case other:
            return Err(f"invalid ICP method: {type_flag}")


def build_icp_registrator(config: dict) -> Result[IncrementalRegistrator, str]:
    """Builds an incremental registrator from a configuration."""

    components: dict = config.get("component_types", None)
    parameters: dict = config.get("component_parameters", None)

    if not components:
        return Err(f"invalid configuration: missing key 'component_types'")
    if not parameters:
        return Err(f"invalid configuration: missing key 'component_parameters'")

    build_funs: dict[str, Callable] = {
        "kernel": add_icp_robust_kernel,
        "estimation_method": add_icp_estimation_method,
        "convergence_criteria": add_icp_convergence_criteria,
    }

    build_results: dict[str, ComponentBuildResult] = {
        key: build_and_validate_component(
            type_flag=components.get(key, None),
            parameters=parameters.get(key, dict()),
            build_fun=build_fun,
        )
        for key, build_fun in build_funs.items()
    }

    components: dict[str, ComponentBuildData] = dict()
    for key, build_result in build_results.items():
        match build_result:
            case Ok(component_data):
                components[key] = component_data
            case Err(message):
                return build_result

    build_state: ICPBuildState = ICPBuildState(**components)

    return compile_icp_registrator(
        build_state=build_state,
        algorithm=config.get("algorithm"),
        parameters=config.get("parameters"),
    )
