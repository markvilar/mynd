"""Module for various filesystem functionality, such as directory and file search. """

import os

from fnmatch import fnmatch
from functools import partial
from pathlib import Path
from typing import Callable


MatchStrategy = Callable[[Path], bool]


def match_path_by_pattern(path: Path, pattern: str) -> bool:
    """Returns true if the path fits the given pattern."""
    match = fnmatch(path, pattern)
    return match


def match_path_by_extension(path: Path, extensions: list[str]) -> bool:
    """Returns true if the path suffix is in the given list of extensions."""
    return path.suffix in extensions


def find_files(
    directory: Path,
    filter_fun: MatchStrategy,
) -> list[Path]:
    """Finds files in the directory and applies the filter to the selection."""
    entries = os.scandir(directory)
    filepaths = [Path(entry.path) for entry in entries if entry.is_file()]
    filtered = [path for path in filepaths if filter_fun(path)]
    return filtered


def find_files_with_extension(
    directory: Path, extensions: list[str]
) -> list[Path]:
    """Finds files in the directory with any of the given extensions."""
    filter_fun = partial(match_path_by_extension, extensions=extensions)
    return find_files(directory, filter_fun=filter_fun)


def find_files_with_pattern(
    directory: Path,
    pattern: str,
) -> list[Path]:
    """Finds files in the directory which match the pattern."""
    filter_fun = partial(match_path_by_pattern, pattern=pattern)
    return find_files(directory, filter_fun=filter_fun)


def list_directory(directory: Path) -> list[Path]:
    """lists files in a directory."""
    filenames = os.listdir(directory)
    filepaths = [directory / filename for filename in filenames]
    return filepaths
