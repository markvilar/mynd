""" Entry point for the package. """

from argparse import ArgumentParser, Namespace
from functools import partial
from pathlib import Path
from typing import Dict, List

from loguru import logger
from result import Ok, Err, Result

from benthoscan.containers import (
    DataTable,
    read_table,
    FileRegistry,
    create_file_registry,
)

from benthoscan.datatypes.camera_types import CameraAssemblyFactory
from benthoscan.datatypes.camera_factories import create_assemblies_from_table
from benthoscan.filesystem import find_files_with_extension
from benthoscan.io import read_dict_from_file
from benthoscan.project import load_document, save_document, create_chunk

from benthoscan.tasks.setup.setup_task import configure_chunk


def create_argument_parser() -> ArgumentParser:
    """Creates a parser and adds arguments to it."""
    parser = ArgumentParser()
    parser.add_argument("document", type=Path, help="metashape document path")
    parser.add_argument("images", type=Path, help="image directory path")
    parser.add_argument("references", type=Path, help="camera reference path")
    parser.add_argument(
        "config",
        type=Path,
        help="configuration file path",
    )
    parser.add_argument(
        "name",
        type=str,
        help="chunk name",
    )
    return parser


def validate_arguments(arguments: Namespace) -> Result[Namespace, str]:
    """Validates the provided command line arguments."""
    if not arguments.document.exists():
        return Err(f"document file does not exist: {arguments.document}")
    if not arguments.images.exists():
        return Err(f"image directory does not exist: {arguments.images}")
    if not arguments.references.exists():
        return Err(f"camera file does not exist: {arguments.references}")
    if not arguments.config.exists():
        return Err(f"camera file does not exist: {arguments.config}")
    return Ok(arguments)


def main():
    """Executed when the script is invoked."""

    parser = create_argument_parser()

    arguments: Namespace = validate_arguments(parser.parse_args()).unwrap()

    logger.info(f"Add chunks:")
    logger.info(f"document: {arguments.document.name}")
    logger.info(f"images:   {arguments.images.name}")
    logger.info(f"cameras:  {arguments.references.name}")
    logger.info(f"config:   {arguments.config.name}")

    # Load document and configuration
    document: Document = load_document(arguments.document).unwrap()
    config: Dict = read_dict_from_file(arguments.config).unwrap()

    # Read table and create camera assemblies
    table: DataTable = read_table(arguments.references).unwrap()
    assembly_factory: CameraAssemblyFactory = partial(
        create_assemblies_from_table,
        table,
        config["cameras"],
        config["assembly"],
    )

    # Find image files in directory
    image_files: List[Path] = find_files_with_extension(
        directory=arguments.images,
        extensions=[".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    # Create file registry and add image files
    file_registry: FileRegistry = create_file_registry()
    file_registry.add_files(image_files)

    # Create chunk
    chunk = create_chunk(document, arguments.name)

    # Configure chunk with images and references
    configure_chunk(chunk, assembly_factory, file_registry)

    # Save document
    save_document(document, arguments.document)


if __name__ == "__main__":
    main()
