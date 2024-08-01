"""Module for reconstruction task config types."""

from dataclasses import dataclass
from pathlib import Path

@dataclass
class ReconstructionConfig:
    """TODO"""

    document_path: Path
    target_labels: list[str]
    processors: dict[str, list]

    # TODO: Add reconstruction pipeline
