""" This module contains a registry for registering files. """

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, TypeAlias


@dataclass
class FileRegistry:
    """Registry for file paths. The registered files are stored in a map with
    string keys that can be used for looking up."""

    FileKey: TypeAlias = str
    files: Dict[FileKey, Path] = field(default_factory=dict)

    def __len__(self) -> int:
        """Returns the number of files in the registry."""
        return len(self.files)

    def __contains__(self, key: FileKey) -> bool:
        """Returns the number of files in the registry."""
        return key in self.files

    def __getitem__(self, key: FileKey) -> Path:
        """Returns the path for the given file key."""
        return self.files[key]

    @property
    def file_paths(self) -> List[Path]:
        """Returns the paths for the registered files."""
        return list(self.files.values())

    @property
    def file_keys(self) -> List[FileKey]:
        """Returns the keys for the registered files."""
        return list(self.files.keys())

    # TODO: Add label strategy
    def add_files(self, files: List[Path]) -> None:
        """Adds the files to the registry. The files are labelled with their
        filename."""
        labelled_files = {path.name: path for path in files}
        self.add_labelled_files(labelled_files)

    def add_labelled_files(self, files: Dict[FileKey, Path]) -> None:
        """Adds labelled files to the registry."""
        self.files.update(files)


def create_file_registry() -> FileRegistry:
    """Default factory method for a file registry."""
    return FileRegistry()
