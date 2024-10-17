"""Module for generic composition functionality."""

from collections.abc import Iterable, Mapping
from typing import Callable, Optional, TypeVar

K: TypeVar = TypeVar("K")
V: TypeVar = TypeVar("V")
R: TypeVar = TypeVar("R")

ComponentMap = Mapping[K, V]
Factory = Callable[[ComponentMap], R]
Labeller = Callable[[ComponentMap], str]

Builder = Callable[[Iterable[ComponentMap]], list[R] | dict[str, R]]


def create_composite_builder(
    factory: Factory,
    labeller: Optional[Labeller] = None,
) -> Builder:
    """Creates a builder method to build composite from component maps. If a
    labeller is given, the builder creates a dictionary of labelled composites.
    """

    def build_composites(
        collections: list[ComponentMap],
    ) -> list[R] | dict[str, R]:
        """Builds image composite loaders from a collection of image components."""

        if labeller is not None:
            composites: dict[str, R] = {
                labeller(components): factory(components)
                for components in collections
            }
        else:
            composites: list[R] = [
                factory(components) for components in collections
            ]

        return composites

    return build_composites
