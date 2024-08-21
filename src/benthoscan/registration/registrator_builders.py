"""Module for building point cloud registrators."""

import functools
import inspect

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any, Optional

from result import Ok, Err, Result


from .feature_registrators import (
    create_fpfh_extractor,
    generate_correspondence_validators,
    create_point_to_point_estimator,
    create_point_to_plane_estimator,
    create_ransac_convergence_criteria,
    create_ransac_registrator,
)

from .incremental_registrators import (
    create_generalized_icp_estimator,
    create_colored_icp_estimator,
    create_icp_convergence_criteria,
    create_tukey_loss,
    create_huber_loss,
    create_regular_icp_registrator,
    create_colored_icp_registrator,
)

from .point_cloud_processors import (
    create_downsampler,
    create_normal_estimator,
)

from .processor_types import (
    PointCloudProcessor,
    GlobalRegistrator,
    IncrementalRegistrator,
)

from ..utils.log import logger


FEATURE_REGISTRATOR_ALGORITHMS = ["feature_matching_ransac"]
ICP_REGISTRATOR_ALGORITHMS = ["icp", "colored_icp", "generalized_icp"]


@dataclass
class ComponentBuildData:
    """Class representing build data for a component."""

    factory: Callable
    parameters: dict[str, Any]


ComponentBuildResult = Result[ComponentBuildData, str]


def validate_build_component(
    build_data: ComponentBuildData,
) -> Result[ComponentBuildData, str]:
    """Validates the build data of a component by checking that required arguments are provided,
    and that the provided parameters are valid function arguments."""

    fun_name: str = build_data.factory.__name__
    signature: inspect.Signature = inspect.signature(build_data.factory)

    required_parameters: list[str] = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect.Parameter.empty
    ]

    # Check the provided parameters are valid arguments
    invalid_parameters: list[str] = list()
    for parameter in build_data.parameters:
        if parameter not in signature.parameters:
            invalid_parameters.append(parameter)

    # Check that required arguments are provided by the parameters
    missing_parameters: list[str] = list()
    for parameter in required_parameters:
        if parameter not in build_data.parameters:
            missing_parameters.append(parameter)

    if invalid_parameters:
        return Err(f"invalid parameters for '{fun_name}': {invalid_parameters}")
    if missing_parameters:
        return Err(f"missing required parameter for '{fun_name}': {missing_parameters}")

    return Ok(build_data)


ComponentBuilder = Callable[[None], ComponentBuildResult]


def build_components_and_compose(
    state_type: type,
    build_funs: dict[str, ComponentBuilder],
    compose_fun: Callable[[object], Result[[object], str]],
) -> Result[[object], str]:
    """Builds a collection of components and composes them into a composition."""

    build_results: dict[str, ComponentBuildResult] = {
        key: build_fun() for key, build_fun in build_funs.items()
    }

    validation_results: dict[str, ComponentBuildResult] = dict()
    for key, build_result in build_results.items():
        match build_result:
            case Ok(component_data):
                validation_results[key] = validate_build_component(component_data)
            case Err(message):
                return build_result
            case _:
                return Err("unknown build error")

    components: dict[str, ComponentBuildData] = dict()
    for key, result in validation_results.items():
        match result:
            case Ok(component_data):
                components[key] = component_data
            case Err(message):
                logger.error(f"invalid component: {message}")
                return result

    try:
        build_state: object = state_type(**components)
    except TypeError as error:
        return Err(f"invalid state components: {error}")

    return compose_fun(build_state)


def build_point_cloud_processor(
    method: str,
    parameters: dict[str, Any],
) -> Result[PointCloudProcessor, str]:
    """Builds a point cloud preprocessor from a configuration."""

    # TODO: Validate parameters
    match method:
        case "downsample":
            processor: PointCloudProcessor = create_downsampler(**parameters)
            return Ok(processor)
        case "estimate_normals":
            processor: PointCloudProcessor = create_normal_estimator(**parameters)
            return Ok(processor)
        case _:
            return Err(f"invalid point cloud processor: {method}")


@dataclass
class FeatureRegistratorBuildState:
    """Class representing a feature registrator build state."""

    feature_extractor: ComponentBuildData
    estimation_method: ComponentBuildData
    validators: ComponentBuildData
    convergence_criteria: ComponentBuildData
    kernel: Optional[ComponentBuildData] = None


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
        case _:
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
        case _:
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
        case _:
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
        case _:
            return Err(f"invalid convergence convergence_criteria: {type_flag}")

    return Ok(ComponentBuildData(factory=factory, parameters=parameters))


def compile_feature_registrator(
    build_state: FeatureRegistratorBuildState,
    algorithm: str,
    parameters: dict[str, Any],
) -> Result[GlobalRegistrator, str]:
    """Compiles a feature registrator based on the given build state."""

    try:
        feature_extractor = build_state.feature_extractor.factory(
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
            registrator = create_ransac_registrator(
                parameters,
                feature_extractor,
                estimation_method,
                validators,
                convergence_criteria,
            )
            return Ok(registrator)
        case _:
            return Err("invalid feature registration algorithm: {algorithm}")


def build_feature_registrator(config: dict) -> Result[GlobalRegistrator, str]:
    """Builds a registration process, i.e. preprocessors and registrator, from a
    configuration."""

    types: dict[str, str] = config.get("component_types", dict())
    parameters: dict[str, dict] = config.get("component_parameters", dict())

    if not types:
        return Err("invalid configuration: missing key 'component_types'")
    if not parameters:
        return Err("invalid configuration: missing key 'component_parameters'")

    build_funs: dict[str, Callable] = {
        "feature_extractor": add_feature_extractor,
        "estimation_method": add_feature_estimation_method,
        "validators": add_feature_validators,
        "convergence_criteria": add_feature_convergence_criteria,
    }

    component_builders: dict[str, Callable] = {
        key: functools.partial(
            build_fun,
            type_flag=types.get(key, None),
            parameters=parameters.get(key, dict()),
        )
        for key, build_fun in build_funs.items()
    }

    composer = functools.partial(
        compile_feature_registrator,
        algorithm=config.get("algorithm"),
        parameters=config.get("parameters"),
    )

    return build_components_and_compose(
        state_type=FeatureRegistratorBuildState,
        build_funs=component_builders,
        compose_fun=composer,
    )


@dataclass
class ICPBuildState:
    """Class representing a ICP build state."""

    estimation_method: ComponentBuildData
    convergence_criteria: ComponentBuildData
    kernel: Optional[ComponentBuildData] = None


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
        case _:
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
        case _:
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
    type_flag: str,
    parameters: dict[str, Any],
) -> Result[IncrementalRegistrator, str]:
    """Sets up an ICP callable with the given parameters."""

    if not build_state.estimation_method:
        return Err("missing ICP estimation method")
    if not build_state.convergence_criteria:
        return Err("missing ICP convergence convergence_criteria")

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

    match type_flag:
        case "icp":
            registrator: IncrementalRegistrator = create_regular_icp_registrator(
                estimation_method=estimation_method,
                convergence_criteria=convergence_criteria,
                parameters=parameters,
            )
            return Ok(registrator)
        case "colored_icp":
            registrator: IncrementalRegistrator = create_colored_icp_registrator(
                estimation_method=estimation_method,
                convergence_criteria=convergence_criteria,
                parameters=parameters,
            )
            return Ok(registrator)
        case _:
            return Err(f"invalid ICP method: {type_flag}")


def build_icp_registrator(config: dict) -> Result[IncrementalRegistrator, str]:
    """Builds an incremental registrator from a configuration."""

    types: dict[str, str] = config.get("component_types", dict())
    parameters: dict[str, dict] = config.get("component_parameters", dict())

    if not types:
        return Err("invalid configuration: missing key 'component_types'")
    if not parameters:
        return Err("invalid configuration: missing key 'component_parameters'")

    build_funs: dict[str, Callable] = {
        "kernel": add_icp_robust_kernel,
        "estimation_method": add_icp_estimation_method,
        "convergence_criteria": add_icp_convergence_criteria,
    }

    component_builders: dict[str, Callable] = {
        key: functools.partial(
            build_fun,
            type_flag=types.get(key, None),
            parameters=parameters.get(key, dict()),
        )
        for key, build_fun in build_funs.items()
    }

    composer = functools.partial(
        compile_icp_registrator,
        algorithm=config.get("algorithm"),
        parameters=config.get("parameters"),
    )

    return build_components_and_compose(
        state_type=ICPBuildState,
        build_funs=component_builders,
        compose_fun=composer,
    )
