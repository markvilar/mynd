"""Module for handling arguments for creating documents and chunks. The module is parses arguments 
and creates configurations based on the arguments."""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from loguru import logger
from result import Ok, Err, Result

from benthoscan.io import read_toml

from .config import (
    ChunkConfig,
    DocumentConfig,
    ProjectConfig,
    create_document_config,
    create_chunk_config,
)


def create_argument_parser() -> ArgumentParser:
    """Creates an argument parser with task specific arguments."""
    parser = ArgumentParser()

    # Document arguments
    parser.add_argument("document", type=Path, help="metashape document path")
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


def parse_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """Creates an argument parser and parses the given arguments."""
    parser = create_argument_parser()
    namespace = parser.parse_args(arguments)

    if not namespace:
        return Err(f"failed to parse arguments: {arguments}")

    return Ok(namespace)


def create_config_from_arguments(arguments: list[str]) -> Result[ProjectConfig, str]:
    """Creates a project configuration from command line arguments."""

    parse_result: Result[Namespace, str] = parse_arguments(arguments)
    if parse_result.is_err():
        return parse_result

    namespace: Namespace = parse_result.ok()

    read_result: Result[dict, str] = read_toml(namespace.chunks)
    if read_result.is_err():
        return read_result

    file_entries = read_result.ok()

    # Create document configuration
    document_config: DocumentConfig = create_document_config(
        namespace.document, namespace.new
    )

    # Create chunk configuration
    chunk_configs: list[ChunkConfig] = list()
    for entry in file_entries["chunk"]:
        chunk_configs.append(
            ChunkConfig(
                entry["name"], entry["directories"], entry["files"], entry["settings"]
            )
        )

    return Ok(ProjectConfig(document=document_config, chunks=chunk_configs))
