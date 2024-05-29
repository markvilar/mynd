"""Module for task configuration for creating documents and chunks."""

from dataclasses import dataclass, field
from pathlib import Path

from result import Ok, Err, Result

from benthoscan.io import read_toml


@dataclass
class ChunkConfig:
    """Class representing a chunk configuration."""

    chunk_name: str
    image_directory: Path
    camera_file: Path
    camera_settings: Path


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


def create_project_config(
    document: Path, 
    create_new: bool, 
    data_directory: Path, 
    chunk_config: Path
) -> Result[ProjectConfig, str]:
    """Creates a project configuration consisting of document and chunk configurations."""

    document_config: DocumentConfig = DocumentConfig(document, create_new)

    read_result: Result[dict, str] = read_toml(chunk_config)
    if read_result.is_err():
        return read_result

    config: dict = read_result.ok()

    chunk_configs: list[ChunkConfig] = list()
    for chunk in config["chunk"]:
        chunk_config: ChunkConfig = ChunkConfig(
            chunk_name = chunk["name"],
            image_directory = data_directory / Path(chunk["image_directory"]),
            camera_file = data_directory / Path(chunk["camera_file"]),
            camera_settings = Path(chunk["camera_settings"])
        )

        chunk_configs.append(chunk_config)

    return Ok(ProjectConfig(document=document_config, chunks=chunk_configs))
