"""Module for reconstruction task config types."""

from dataclasses import dataclass

from benthoscan.project import Chunk, Document


@dataclass
class ReconstructionConfig:
    """TODO"""

    document: Document
    target_labels: list[str]
    processors: dict[str, list]

    # TODO: Add reconstruction pipeline
