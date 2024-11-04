"""Module for registration pipeline functionality."""

from dataclasses import dataclass, field

from mynd.geometry import PointCloud

from .data_types import RigidTransformation, RegistrationResult

from .processor_types import (
    PointCloudProcessor,
    GlobalRegistrator,
    IncrementalRegistrator,
)

GLOBAL_MODULE_KEY: str = "global_module"
LOCAL_MODULE_KEY: str = "local_module"


@dataclass
class RegistrationConfig:
    """Class representing a registration configuration."""

    @dataclass
    class Module:
        """Class representing a config item."""

        preprocessor: list[dict]
        registrator: dict

    global_module: Module
    local_modules: list[Module]


def create_registration_config(config: dict) -> RegistrationConfig:
    """Creates a registration pipeline config."""
    initializer: RegistrationConfig.Module = RegistrationConfig.Module(
        **config.get("global")
    )
    if "incrementors" in config:
        incrementors: list[RegistrationConfig.Module] = [
            RegistrationConfig.Module(**item)
            for item in config.get("incrementors")
        ]
    else:
        incrementors: list = list()
    return RegistrationConfig(initializer, incrementors)


@dataclass
class RegistrationPipeline:
    """Class representing a registration pipeline."""

    @dataclass
    class InitializerModule:
        """Class representing an initializer module."""

        preprocessor: PointCloudProcessor
        registrator: GlobalRegistrator

    @dataclass
    class IncrementorModule:
        """Class representing an incrementor module."""

        preprocessor: PointCloudProcessor
        registrator: IncrementalRegistrator

    initializer: InitializerModule
    incrementors: list[IncrementorModule] = field(default_factory=list)


def apply_registration_pipeline(
    pipeline: RegistrationPipeline, source: PointCloud, target: PointCloud
) -> RegistrationResult:
    """Applies a registration pipeline to the source and target."""

    result: RegistrationResult = _apply_initializer(
        pipeline.initializer, source=source, target=target
    )

    for incrementor in pipeline.incrementors:
        result: RegistrationResult = _apply_incrementor(
            incrementor,
            source=source,
            target=target,
            transformation=result.transformation,
        )

    return result


def _apply_initializer(
    module: RegistrationPipeline.InitializerModule,
    source: PointCloud,
    target: PointCloud,
) -> RegistrationResult:
    """Applies an initializer module to the source and target."""

    source_pre: PointCloud = module.preprocessor(source)
    target_pre: PointCloud = module.preprocessor(target)

    return module.registrator(source=source_pre, target=target_pre)


def _apply_incrementor(
    module: RegistrationPipeline.IncrementorModule,
    source: PointCloud,
    target: PointCloud,
    transformation: RigidTransformation,
) -> RegistrationResult:
    """Applies an incrementor module to the source and target."""

    source_pre: PointCloud = module.preprocessor(source)
    target_pre: PointCloud = module.preprocessor(target)

    result: RegistrationResult = module.registrator(
        source=source_pre,
        target=target_pre,
        transformation=transformation,
    )

    return result
