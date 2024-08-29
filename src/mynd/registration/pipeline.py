"""Module for registration pipeline functionality."""

import inspect
import typing

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Optional, Self

import numpy as np

from ..geometry import PointCloud
from ..utils.log import logger

from .data_types import RegistrationResult
from .processor_types import (
    PointCloudProcessor,
    GlobalRegistrator,
    IncrementalRegistrator,
)


def get_required_parameters(func: Callable) -> list[str]:
    """Returns the required parameters from a callable."""
    signature: inspect.Signature = inspect.signature(func)

    required_parameters = [
        name
        for name, parameter in signature.parameters.items()
        if parameter.default == inspect.Parameter.empty
    ]

    return required_parameters


@dataclass
class Module:
    """Class representing a stand-alone registration module."""

    registrator: GlobalRegistrator | IncrementalRegistrator
    preprocessors: list[PointCloudProcessor] = field(default_factory=list)
    requires_transformation: bool = False

    def __post_init__(self: Self) -> Self:
        """TODO"""

        # TODO: Remove
        required_parameters: list = get_required_parameters(self.registrator)
        _test = typing.get_type_hints(GlobalRegistrator)

        match required_parameters:
            case ["source", "target", "transformation"]:
                self.requires_transformation = True
            case ["source", "target"]:
                self.requires_transformation = False

        return self

    def preprocess(self: Self, cloud: PointCloud) -> PointCloud:
        """Applies the preprocessors to a point cloud."""
        for preprocessor in self.preprocessors:
            cloud: PointCloud = preprocessor(cloud)

        return cloud

    def forward(
        self: Self,
        source: PointCloud,
        target: PointCloud,
        transformation: Optional[np.ndarray] = None,
    ) -> RegistrationResult:
        """Applies the preprocessors to the point clouds and registers the source to the target."""

        source: PointCloud = self.preprocess(source)
        target: PointCloud = self.preprocess(target)

        if isinstance(transformation, np.ndarray):
            result: RegistrationResult = self.registrator(
                source=source,
                target=target,
                transformation=transformation,
            )
        else:
            result: RegistrationResult = self.registrator(source=source, target=target)

        return result


@dataclass
class ModuleList:
    """Class representing a list of registration modules."""

    modules: list[tuple[str, Module]] = field(default_factory=list)

    def __init__(self: Self, modules: list[Module]) -> Self:
        """TODO"""

        # TODO: Validate input/output
        self.modules = list()

        for module in modules:
            type_hints = typing.get_type_hints(module.registrator)

            match type_hints:
                case {
                    "source": source,
                    "target": target,
                    "transformation": transformation,
                }:
                    if (
                        source == PointCloud
                        and target == PointCloud
                        and transformation == np.ndarray
                    ):
                        self.modules.append(("incremental", module))
                    else:
                        logger.error(f"invalid registrator module: {module}")
                case {"source": source, "target": target}:
                    if source == PointCloud and target == PointCloud:
                        self.modules.append(("global", module))
                case _:
                    logger.error(f"invalid registrator module: {module}")

    def __iter__(self) -> tuple[str, Module]:
        """Iterates over the modules in the module list."""
        for item in self.modules:
            yield item


ResultCallback = Callable[[PointCloud, PointCloud, RegistrationResult], None]


def apply_registration_modules(
    modules: ModuleList,
    source: PointCloud,
    target: PointCloud,
    callback: Optional[ResultCallback] = None,
) -> None:
    """Registers a point cloud source to a target by applying the modules in sequential order.
    If a callback is provided,"""

    results: dict[int, RegistrationResult] = dict()
    transformation: np.ndarray = np.identity(4)

    for index, (flag, module) in enumerate(modules):

        # TODO: Add more robust switch method than a string flag
        match flag:
            case "global":
                result: RegistrationResult = module.forward(source, target)
            case "incremental":
                result: RegistrationResult = module.forward(
                    source, target, transformation
                )
            case other:
                raise NotImplementedError(f"invalid registrator type: {other}")

        results[index] = result
        transformation: np.ndarray = result.transformation

        if callback:
            callback(module.preprocess(source), module.preprocess(target), result)

    return results
