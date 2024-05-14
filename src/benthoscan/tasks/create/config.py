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
        data: Path

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


def create_chunk_config(
    name: str,
    directories: dict[str, Path],
    files: dict[str, str],
    settings: dict[str, Path],
) -> ChunkConfig:
    """Creates a chunk configuration object."""

    directories: ChunkConfig.Directories = ChunkConfig.Directories(
        images=Path(directories["images"]),
        data=Path(directories["data"]),
    )

    files: ChunkConfig.Files = ChunkConfig.Files(
        cameras=str(files["cameras"]), references=str(files["references"])
    )

    settings: ChunkConfig.Settings = ChunkConfig.Settings(
        cameras=Path(settings["cameras"]),
        references=Path(settings["references"]),
    )

    return ChunkConfig(
        name=name,
        directories=directories,
        files=files,
        settings=settings,
    )


def create_document_config(path: Path, create_new: bool) -> DocumentConfig:
    """Create a document configuration object."""
    return DocumentConfig(path, create_new)
