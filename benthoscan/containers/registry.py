""" This module contains a registry for registering files. """

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, TypeAlias, TypeVar, Generic


Key = TypeVar("Key")
Value = TypeVar("Value")


@dataclass
class Registry(Generic[Key, Value]):
    """Generic registry class."""

    items: Dict[Key, Value] = field(default_factory=dict)

    def __len__(self) -> int:
        """Returns the number of items in the registry."""
        return len(self.items)

    def __contains__(self, key: Key) -> bool:
        """Returns the number of items in the registry."""
        return key in self.items

    def __getitem__(self, key: Key) -> Value:
        """Returns the value for the given key."""
        return self.items[key]

    def __setitem__(self, key: Key, value: Value) -> None:
        """Inserts a key value pair in the registry."""
        self.items[key] = value

    @property
    def values(self) -> List[Value]:
        """Returns the values for the registered items."""
        return list(self.items.values())

    @property
    def keys(self) -> List[Key]:
        """Returns the keys for the registered items."""
        return list(self.items.keys())

    def insert(self, key: Key, value: Value) -> None:
        """Insert a key value pair in the registry."""
        self.items[key] = value

    def remove(self, key: Key) -> None:
        """Removes a key value pair in the registry."""
        self.items.pop(key)

    def pop(self, key: Key) -> Value:
        """Insert a key value pair in the registry."""
        return self.items.pop(key)


def create_registry() -> Registry[Key, Value]:
    """Default factory method for a registry."""
    return Registry[Key, Value]()
