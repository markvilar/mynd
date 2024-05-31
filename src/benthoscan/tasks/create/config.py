"""Module for task configuration for creating documents and chunks."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChunkConfig:
    """Class representing a chunk configuration."""

    @dataclass
    class Directories:
        """Class representing chunk directories."""

        images: Path
        cameras: Path

    @dataclass
    class Files:
        """Class representing chunk files."""

        cameras: str
        references: str

    @dataclass
    class Settings:
        """Class representing chunk settings."""

        cameras: Path
        references: Path

    name: str

    directories: Directories
    files: Files
    settings: Settings

    # NOTE: Consider adding camera calibration file


@dataclass
class DocumentConfig:
    """Class representing a document configuration."""

    path: Path
    create_new: bool


@dataclass
class ProjectConfig:
    """Class representing a project configuration."""

    document: DocumentConfig
    chunks: list[ChunkConfig] = field(default_factory=list)
