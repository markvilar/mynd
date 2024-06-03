""" This module contains a registry for registering files. """

from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeAlias, TypeVar, Generic, Callable


Key = TypeVar("Key")
Value = TypeVar("Value")


@dataclass
class Registry(Generic[Key, Value]):
    """Generic registry class."""

    _items: dict[Key, Value] = field(default_factory=dict)

    def __len__(self) -> int:
        """Returns the number of items in the registry."""
        return len(self._items)

    def __contains__(self, key: Key) -> bool:
        """Returns the number of items in the registry."""
        return key in self._items

    def __getitem__(self, key: Key) -> Value:
        """Returns the value for the given key."""
        return self._items[key]

    def __setitem__(self, key: Key, value: Value) -> None:
        """Inserts a key value pair in the registry."""
        self._items[key] = value

    @property
    def count(self) -> int:
        """Returns the number of items in the registry."""
        return len(self)

    @property
    def values(self) -> list[Value]:
        """Returns the values for the registered items."""
        return list(self._items.values())

    @property
    def keys(self) -> list[Key]:
        """Returns the keys for the registered items."""
        return list(self._items.keys())

    def items(self) -> list[tuple[Key, Value]]:
        """Returns the items in the registry."""
        return self._items.items()

    def insert(self, key: Key, value: Value) -> None:
        """Insert a key value pair in the registry."""
        self._items[key] = value

    def remove(self, key: Key) -> None:
        """Removes a key value pair in the registry."""
        self._items.pop(key)

    def pop(self, key: Key) -> Value:
        """Insert a key value pair in the registry."""
        return self._items.pop(key)
