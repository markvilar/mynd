"""Module for database I/O functionality."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Self, TypeAlias

import h5py

from ...utils.result import Ok, Err, Result


H5_DATABASE_SUFFIXES: list[str] = [".h5", ".hdf5"]


@dataclass
class H5Database:
    """Class representing a H5 database, encapsulating a H5 file object
    with logical checks and convenient functions."""

    _file: h5py.File

    # TODO: Replace with H5 group encapsulation
    Group: TypeAlias = h5py.Group
    Dataset: TypeAlias = h5py.Dataset

    def __del__(self: Self) -> None:
        """Destructor - closes the database file upon destruction."""
        self._file.close()

    def __contains__(self: Self, key: str) -> bool:
        """Returns true if the key is in the file object."""
        return key in self._file

    @property
    def path(self: Self) -> Path:
        """Returns the path of the file database."""
        return Path(self._file.filename)

    @property
    def root(self: Self) -> Group:
        """Returns the root group of the database."""
        return self._file[self._file.name]

    def list_groups(self: Self) -> list[str]:
        """List the groups in the database."""
        return list(self._file.keys())

    def create_group(self: Self, key: str) -> Result[Group, str]:
        """Creates a group in the file database and returns it."""
        if key in self._file:
            return Err("group is already in database")
        if not isinstance(key, str):
            return Err(f"invalid group key type: {type(key)}")
        return Ok(self._file.create_group(key))

    def delete_group(self: Self, key: str) -> None:
        """Deletes the group if the group is deleted, and false otherwise."""
        group = self.get_group(key)
        if group:
            del group

    def get(self: Self, key: str) -> Optional[Group | Dataset]:
        """Returns the group or dataset with the given key."""
        return self._file.get(key)


def create_file_database(
    path: Path, mode: str = "w"
) -> Result[H5Database, str]:
    """Creates a new file database."""

    if not path.parent.exists():
        return Err(f"parent directory does not exist: {path}")
    if path.suffix not in H5_DATABASE_SUFFIXES:
        return Err(
            f"invalid file database suffix: got {path.suffix}, expected {H5_DATABASE_SUFFIXES}"
        )

    return _open_file_database(path, mode=mode)


def load_file_database(path: Path, mode: str = "r+") -> Result[H5Database, str]:
    """Loads an existing file database."""

    if not path.exists():
        return Err(f"path does not exist: {path}")
    if not path.is_file():
        return Err(f"path is not a file: {path}")
    if path.suffix not in H5_DATABASE_SUFFIXES:
        return Err(
            f"invalid file database suffix: got {path.suffix}, expected {*H5_DATABASE_SUFFIXES,}"
        )

    return _open_file_database(path, mode=mode)


def _open_file_database(path: Path, mode: str) -> Result[H5Database, str]:
    """Opens a file database at the given path."""

    try:
        file: h5py.File = h5py.File(name=str(path), mode=mode)
        return Ok(H5Database(file))
    # TODO: Figure out the relevant exceptions
    except BaseException as error:
        return Err(error)
