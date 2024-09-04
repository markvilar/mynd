"""Module for API identifiers."""

from dataclasses import dataclass
from typing import Self


@dataclass(eq=True, frozen=True)
class Identifier:
    """Class representing an identifier with key and label."""

    key: int
    label: str

    def __init__(self: Self, key: int, label: str = "") -> None:
        """Initialization method."""
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
