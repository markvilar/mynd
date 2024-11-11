"""Module for registration utility functionality."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

import numpy as np

from mynd.spatial import decompose_transformation, rotation_matrix_to_euler
from mynd.utils.log import logger

from .data_types import RegistrationResult


T: TypeVar = TypeVar("T")


@dataclass
class RegistrationIndex:
    """Class representing a multi source index used for registration."""

    target: T
    sources: list[T]


def generate_cascade_indices(items: Sequence[T]) -> list[RegistrationIndex]:
    """Generates a list of cascaded multi-source indices."""

    items: list[T] = list(items)

    indices: list[RegistrationIndex] = list()
    for index, target in enumerate(items[:-1]):
        sources: list[T] = items[index + 1 :]
        indices.append(RegistrationIndex(target=target, sources=sources))

    return indices


def log_registration_result(result: RegistrationResult) -> None:
    """Logs a registration result."""

    scale, rotation, translation = decompose_transformation(
        result.transformation
    )

    rotz, roty, rotx = rotation_matrix_to_euler(rotation, degrees=True)

    correspondence_count: int = len(result.correspondence_set)

    np.set_printoptions(precision=3)

    logger.info(f"Corresp.:     {correspondence_count}")
    logger.info(f"Fitness:      {result.fitness:.5f}")
    logger.info(f"Inlier RMSE:  {result.inlier_rmse:.5f}")
    logger.info(f"Scale:        {scale:.3f}")
    logger.info(f"Translation:  {translation}")
    logger.info(f"Rot. ZYX:     {rotz:.2f}, {roty:.2f}, {rotx:.2f}")
