""" Entry point for the package. """
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict, List

from loguru import logger
from result import Ok, Err, Result

from benthoscan.io import read_config
from benthoscan.utils import get_time_string

from benthoscan.reconstruction.chunk import create_chunk
from benthoscan.reconstruction.document import load_document, save_document
from benthoscan.reconstruction.setup import ImageConfig, ReferenceConfig, \
    CameraConfig, ChunkConfig, configure_chunk

def validate_arguments(arguments: Namespace) -> Result[Namespace, str]:
    """ Validates the provided command line arguments. """
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
    """ Executed when the script is invoked. """
    parser = ArgumentParser()
    parser.add_argument("document",
        type = Path,
        help = "metashape document path"
    )
    parser.add_argument("images",
        type = Path,
        help = "image directory path"
    )
    parser.add_argument("references",
        type = Path,
        help = "camera reference path"
    )
    parser.add_argument("config",
        type = Path,
        help = "configuration file path",
    )

    # Validate arguments
    result: Result[Namespace, str] = validate_arguments(parser.parse_args())
    if result.is_err():
        logger.error(f"argument validation error: {result.unwrap()}")
    arguments = result.unwrap()

    logger.info(f"Add chunks:")
    logger.info(f"document: {arguments.document.name}")
    logger.info(f"images:   {arguments.images.name}")
    logger.info(f"cameras:  {arguments.references.name}")
    logger.info(f"config:   {arguments.config.name}")

    # Load document and configuration
    document: Document = load_document(arguments.document).unwrap()
    config: Dict = read_config(arguments.config).unwrap()

    # Configure images, camera, and references
    image_config = ImageConfig(
        directory = arguments.images,
        extensions = [".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )
    camera_config = CameraConfig(
        config["camera_config"]["name"], 
        config["camera_config"]["label_keys"]
    )
    reference_config = ReferenceConfig(
        arguments.references,
        config["reference"]["position_format"],
        config["reference"]["position_fields"],
        config["reference"]["orientation_format"],
        config["reference"]["orientation_fields"]
    )
    chunk_config = ChunkConfig(image_config, camera_config, reference_config)

    # Create chunk
    datetime = get_time_string("YYYYMMDD_hhmmss")
    chunk = create_chunk(document, f"{datetime}_add_chunk_script")
   
    # Configure chunk with images and references
    configure_chunk(chunk, chunk_config)
   
    # Save document
    save_document(document, arguments.document)

if __name__ == "__main__":
    main()
