"""Package for generic data containers."""

from .registry import Registry, create_file_registry_from_directory

__all__ = [
    "Registry",
    "create_file_registry_from_directory",
]