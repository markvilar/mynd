""" Entry point for the package. """
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List

import Metashape

from loguru import logger
from result import Ok, Err, Result


from benthoscan.io import read_csv, read_config
from benthoscan.utils import ArgumentParser, Namespace, get_time_string

from benthoscan.reconstruction.chunk import (
    create_chunk, 
    add_image_groups_to_chunk
)
from benthoscan.reconstruction.document import (
    load_document,
    save_document
)
from benthoscan.reconstruction.reference import (
    Reference, 
    read_reference_from_file
)
from benthoscan.reconstruction.file_group import create_file_groups

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

def configure_chunk(
    chunk: Metashape.Chunk, 
    references: Dict, 
    image_groups: List[Dict[str, Path]],
) -> None:
    """ Configures a chunk. """
    group_order = list(image_groups[0].keys())
    add_image_groups_to_chunk(chunk, image_groups, group_order)

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

    result: Result[Namespace, str] = validate_arguments(parser.parse_args())
    if result.is_err():
        logger.error(f"argument validation error: {result.unwrap()}")

    arguments = result.unwrap()

    # Load document and configuration
    document: Document = load_document(arguments.document)
    config: Dict = read_config(arguments.config)

    logger.info(f"document: {arguments.document}")
    logger.info(f"images:   {arguments.images}")
    logger.info(f"cameras:  {arguments.references}")

    # Load references
    result: Result[Dict, str] = read_reference_from_file(arguments.references)
    if result.is_err():
        logger.error("read references error: {result.unwrap()}")

    references = result.unwrap()

    # TODO: For each camera config - create file groups
    stereo_config = {
        "label" : "auv_stereo",
        "components" : [
            { "stereo_left" : "stereo_left_filename" },
            { "stereo_right" : "stereo_right_filename" },
        ]
    }

    file_groups: List[Dict[str, Path]] = create_file_groups(
        arguments.images,
        references,
        reference_keys = ["stereo_left_filename", "stereo_right_filename"],
    )

    logger.info(f"Desired file groups: {len(references)}")
    logger.info(f"Retrieved file groups: {len(file_groups)}")

    # Create chunk
    datetime = get_time_string("YYYYMMDD_hhmmss")
    chunk = create_chunk(document, f"{datetime}_add_chunk_script")
   
    # TODO: Configure chunk with images and references
    configure_chunk(
        chunk, 
        references, 
        image_groups = file_groups,
    )
   
    # Save document
    save_document(document, arguments.document)

if __name__ == "__main__":
    main()
