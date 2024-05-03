""" Entry point for the package. """

from functools import partial
from pathlib import Path
from typing import Dict, List

from loguru import logger

from benthoscan.containers import DataTable, read_table, Registry, create_registry
from benthoscan.datatypes.camera_types import CameraAssemblyFactory
from benthoscan.datatypes.camera_factories import create_assemblies_from_table

from benthoscan.filesystem import find_files_with_extension
from benthoscan.io import read_dict_from_file
from benthoscan.project import load_document, save_document, create_chunk

from .arguments import create_argument_parser, validate_arguments
from .chunk_setup import configure_chunk


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

    file_registry: Registry[str, Path] = create_registry()
    for file in image_files:
        file_registry.insert(file.name, file)

    # Create chunk
    chunk = create_chunk(document, arguments.name)

    # Configure chunk with images and references
    configure_chunk(chunk, assembly_factory, file_registry)

    # Save document
    save_document(document, arguments.document)


if __name__ == "__main__":
    main()
