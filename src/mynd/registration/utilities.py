"""Module for registration utility functionality."""

from dataclasses import dataclass

from mynd.spatial import decompose_transformation
from mynd.utils.log import logger

from .data_types import RegistrationResult


@dataclass
class MultiTargetIndex:
    """Class representing a multi target index used for registration."""

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


def log_registration_result(
    source: int, target: int, result: RegistrationResult
) -> None:
    """Logs a registration result."""

    scale, rotation, translation = decompose_transformation(
        result.transformation
    )

    logger.info("")
    logger.info(f"Source:           {source}")
    logger.info(f"Target:           {target}")
    logger.info(f"Corresp.:         {len(result.correspondence_set)}")
    logger.info(f"Fitness:          {result.fitness}")
    logger.info(f"Inlier RMSE:      {result.inlier_rmse}")
    logger.info(f"Trans. scale:     {scale}")
    logger.info(f"Trans. trans.:    {translation}")
    logger.info(f"Trans. rot.:      {rotation}")
    logger.info("")
