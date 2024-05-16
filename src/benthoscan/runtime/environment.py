"""Module for runtime environment."""

from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


@dataclass
class Environment:
    """Class representing environment variables."""

    data_directory: Path


def load_environment(path: Path = Path(".env")) -> Environment:
    """Loads variables from an environment file."""
    variables: dict = dotenv_values(path)
    return Environment(data_directory=Path(variables["DATA_DIR"]))
