"""Module for handling arguments for creating documents and chunks. The module is parses arguments 
and creates configurations based on the arguments."""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from loguru import logger
from result import Ok, Err, Result

from benthoscan.io import read_toml
from benthoscan.runtime import load_environment

from .config import ChunkConfig, DocumentConfig, ProjectConfig


def create_argument_parser() -> ArgumentParser:
    """Creates an argument parser with task specific arguments."""
    parser = ArgumentParser()

    # Document arguments
    parser.add_argument("document", type=Path, help="document path")
    parser.add_argument(
        "--new", action=BooleanOptionalAction, help="create new document"
    )

    # Multiple chunk arguments
    parser.add_argument(
        "chunks",
        type=Path,
        default=None,
        help="chunk configuration file",
    )

    return parser


def parse_project_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """Creates an argument parser and parses the given arguments."""
    parser = create_argument_parser()
    namespace = parser.parse_args(arguments)

    if not namespace:
        return Err(f"failed to parse arguments: {arguments}")

    return Ok(namespace)


def create_chunk_config(
    name: str,
    directories: dict[str, Path],
    files: dict[str, Path],
    settings: dict[str, Path],
) -> ChunkConfig:
    """Creates a chunk configuration object."""

    environment: Environment = load_environment()

    directories: ChunkConfig.Directories = ChunkConfig.Directories(
        images=environment.data_directory / Path(directories["images"]),
        cameras=environment.data_directory / Path(directories["cameras"]),
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


def create_chunk_configs_from_file(path: Path) -> list[ChunkConfig]:
    """Creates a collection of chunk configurations from a TOML file."""
    
    # Read chunk configurations from file
    read_result: Result[dict, str] = read_toml(path)
    if read_result.is_err():
        return read_result

    sections: dict = read_result.ok()

    # Create chunk configurations
    configs: list[ChunkConfig] = list()
    for section in sections["chunk"]:
        config: ChunkConfig = create_chunk_config(
            section["name"],
            section["directories"],
            section["files"],
            section["settings"],
        )
        configs.append(config)

    return configs


def configure_project(namespace: Namespace) -> Result[ProjectConfig, str]:
    """Creates a project configuration from command line arguments."""

    # Create document configuration
    document_config: DocumentConfig = create_document_config(
        namespace.document, namespace.new
    )

    chunk_configs: list[ChunkConfig] = create_chunk_configs_from_file(namespace.chunks)

    return Ok(ProjectConfig(document=document_config, chunks=chunk_configs))
