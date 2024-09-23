"""Module for the database ingest facade."""

from dataclasses import dataclass
from pathlib import Path


class CreateDatabaseTask:
    """Facade class for create database tasks."""

    @dataclass
    class Config:
        """Class representing a dataset config."""

        output_path: Path
        group_patterns: dict[str, str]
