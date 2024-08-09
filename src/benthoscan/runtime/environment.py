"""Module for runtime environment."""

import os

from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


CACHE_DIR_KEY: str = "CACHE_DIR"
DEFAULT_CACHE: Path = Path("./.cache")


@dataclass
class Environment:
    """Class representing environment variables."""

    working_directory: Path
    cache_directory: Path = DEFAULT_CACHE


def load_environment(path: Path = Path(".env")) -> Environment:
    """Loads variables from an environment file."""
    variables: dict = dotenv_values(path)

    if CACHE_DIR_KEY in variables:
        cache_path: Path = Path(variables[CACHE_DIR_KEY])
    else:
        cache_path: Path = DEFAULT_CACHE

    environment: Environment = Environment(
        cache_directory=cache_path,
        working_directory=Path(os.getcwd()),
    )

    return environment
