"""Module for various filesystem functionality, such as directory and file search. """

import glob

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Self, TypeVar


def list_directory(directory: Path, pattern: str = "*") -> list[Path]:
    """List files in a directory."""
    return [Path(path) for path in glob.glob(f"{directory}/{pattern}")]


def search_files(search_string: str) -> list[Path]:
    """Searches for files with the given search string."""
    return [Path(path) for path in glob.glob(search_string)]


@dataclass(frozen=True)
class Resource:
    """Class representing a file resource which is either a local file,
    a local directory."""

    _handle: Path

    @property
    def handle(self: Self) -> Path:
        """Returns the resource handle."""
        return self._handle

    @property
    def stem(self: Self) -> str:
        """Returns the stem of the resource handle."""
        return self._handle.stem

    def is_file(self: Self) -> bool:
        """Returns true if the resource is a file."""
        if isinstance(self._handle, Path):
            return self._handle.is_file()
        else:
            return False

    def is_directory(self: Self) -> bool:
        """Returns true if the resource is a directory."""
        if isinstance(self._handle, Path):
            return self._handle.is_dir()
        else:
            return False


def create_resource(handle: Path) -> Optional[Resource]:
    """Creates a resource from a path. The given path must exist in order to create a resource."""
    if not handle.exists():
        return None
    return Resource(handle)


ResourceLabeller = Callable[[Path], str]


def label_resource_by_stem(resource: Resource) -> str:
    """Default labeller for the resource manager."""
    if resource.is_file():
        return resource.handle.stem
    elif resource.is_directory():
        return resource.handle.stem
    else:
        raise NotImplementedError("invalid resource")


@dataclass(frozen=True)
class ResourceID:
    """Class representing a resource identifier."""

    key: int
    label: str


@dataclass
class ManagedResource:
    """Class representing a managed resource."""

    identifier: ResourceID
    resource: Resource
    tags: set[str] = field(default_factory=set)


@dataclass
class ResourceManager:
    """Class representing a resource manager."""

    _current_key: int = 0
    _resources: dict[ResourceID, ManagedResource] = field(default_factory=dict)
    _labeller: ResourceLabeller = label_resource_by_stem

    def _get_key(self: Self) -> int:
        """Returns a key and increments the current key."""
        key: int = self._current_key
        self._current_key += 1
        return key

    def get_identifiers(self: Self) -> list[ResourceID]:
        """Gets the resource identifier from the manager."""
        return list(self._resources.keys())

    def get_resource(self: Self, identifier: ResourceID) -> Optional[Resource]:
        """Gets the resource from the"""
        managed_resource: ManagedResource = self._resources.get(identifier)
        if managed_resource is None:
            return None
        return managed_resource.resource

    def add_resource(
        self: Self,
        resource: Resource,
        tags: Iterable[str] = list(),
        labeller: Optional[ResourceLabeller] = None,
    ) -> None:
        """Adds a resource to the manager."""

        key: int = self._get_key()

        if not isinstance(tags, set):
            tags: set[str] = set(tags)

        if labeller is None:
            labeller = self._labeller

        label: str = labeller(resource)
        identifier: ResourceID = ResourceID(key, label)
        managed_resource: ManagedResource = ManagedResource(
            identifier, resource, tags
        )
        self._resources[identifier] = managed_resource

    def add_resources(
        self: Self,
        resources: Iterable[Resource],
        tags: Iterable[str] = list(),
        labeller: Optional[ResourceLabeller] = None,
    ) -> None:
        """Adds a collection of resources to the manager."""

        for resource in resources:
            self.add_resource(resource, tags, labeller)

    def query_tags(self: Self, tags: Iterable[str]) -> list[Resource]:
        """Query resources based on their tags."""

        if not isinstance(tags, set):
            tags: set[str] = set(tags)

        selected_resources: list[Resource] = [
            managed_resource.resource
            for identifier, managed_resource in self._resources.items()
            if tags.issubset(managed_resource.tags)
        ]

        return selected_resources


T: TypeVar = TypeVar("T")

Resources = list[Resource]
ComponentGroups = Mapping[T, Resources]
ComponentMatch = Mapping[T, Resource]


def match_resources_by_stem(
    component_groups: ComponentGroups,
) -> list[ComponentMatch]:
    """Matches resources of different types based on common stems."""
    matches: dict[str, ComponentMatch] = dict()
    for key, resources in component_groups.items():

        for resource in resources:
            if resource.stem not in matches:
                matches[resource.stem] = dict()

            matches[resource.stem][key] = resource

    matches: list[ComponentMatch] = list(matches.values())
    return matches


def check_match_has_all_components(
    components: ComponentMatch,
    required_keys: set[T],
) -> bool:
    """Check if image matches has the required components."""
    return set(components.keys()) == required_keys


ResourceMatchValidator = Callable[[ComponentMatch], bool]
ResourceMatcher = Callable[[ComponentGroups], list[ComponentMatch]]


def create_resource_matcher(
    matcher: ResourceMatcher = match_resources_by_stem,
    validator: Optional[ResourceMatchValidator] = None,
) -> Callable:
    """Creates a resource matcher."""

    def match_resources(
        component_groups: ComponentGroups,
    ) -> list[ComponentMatch]:
        """Matches resources from different groups."""
        component_matches: list[ComponentMatch] = matcher(component_groups)

        if validator is None:
            return component_matches

        return [
            components
            for components in component_matches
            if validator(components)
        ]

    return match_resources
