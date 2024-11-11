"""Module for registration pipeline functionality."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeAlias

from mynd.geometry import PointCloud, PointCloudProcessor

from .data_types import RigidTransformation, RegistrationResult
from .registrator_types import PointCloudAligner, PointCloudRefiner


@dataclass
class RegistrationPipeline:
    """Class representing a registration pipeline."""

    @dataclass
    class AlignerModule:
        """Class representing an initializer module."""

        preprocessor: PointCloudProcessor
        registrator: PointCloudAligner

    @dataclass
    class RefinerModule:
        """Class representing an incrementor module."""

        preprocessor: PointCloudProcessor
        registrator: PointCloudRefiner

    initializer: AlignerModule
    incrementors: list[RefinerModule] = field(default_factory=list)


RegistrationCallback: TypeAlias = Callable[
    [PointCloud, PointCloud, RegistrationResult], None
]


def apply_registration_pipeline(
    pipeline: RegistrationPipeline,
    source: PointCloud,
    target: PointCloud,
    callback: RegistrationCallback | None = None,
) -> RegistrationResult:
    """Applies a registration pipeline to the source and target."""

    result: RegistrationResult = _apply_aligner_module(
        pipeline.initializer,
        source=source,
        target=target,
        callback=callback,
    )

    for incrementor in pipeline.incrementors:
        result: RegistrationResult = _apply_refiner_module(
            incrementor,
            source=source,
            target=target,
            transformation=result.transformation,
            callback=callback,
        )

    return result


def _apply_aligner_module(
    module: RegistrationPipeline.AlignerModule,
    source: PointCloud,
    target: PointCloud,
    callback: RegistrationCallback | None = None,
) -> RegistrationResult:
    """Applies an initializer module to the source and target."""

    source_pre: PointCloud = module.preprocessor(source)
    target_pre: PointCloud = module.preprocessor(target)

    result: RegistrationResult = module.registrator(
        source=source_pre, target=target_pre
    )

    if callback is not None:
        callback(source_pre, target_pre, result)

    return result


def _apply_refiner_module(
    module: RegistrationPipeline.RefinerModule,
    source: PointCloud,
    target: PointCloud,
    transformation: RigidTransformation,
    callback: RegistrationCallback | None = None,
) -> RegistrationResult:
    """Applies an incrementor module to the source and target."""

    source_pre: PointCloud = module.preprocessor(source)
    target_pre: PointCloud = module.preprocessor(target)

    result: RegistrationResult = module.registrator(
        source=source_pre,
        target=target_pre,
        transformation=transformation,
    )

    if callback is not None:
        callback(source_pre, target_pre, result)

    return result
