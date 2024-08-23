"""Module for registration utility functionality."""

from dataclasses import dataclass


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
