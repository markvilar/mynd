"""Module for a generic pair class."""

import typing


T = typing.TypeVar("T")


class Pair(typing.NamedTuple, typing.Generic[T]):
    """Class representing a pair of items."""

    first: T
    second: T
