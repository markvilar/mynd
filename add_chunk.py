""" Entry point for the package. """
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List

import Metashape

from loguru import logger
from result import Ok, Err, Result

from benthoscan.core.filesystem import (
    find_files_with_extension,
    find_files_with_pattern
)
from benthoscan.core.io import read_csv, read_config
from benthoscan.core.utils import ArgumentParser, Namespace, get_time_string

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
from benthoscan.reconstruction.image_group import (
    create_target_images_from_reference,
    match_files,
    Table,
)

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
    image_groups: List[OrderedDict], # TODO: ImageGroupLoader
    image_files: List[Path]
) -> None:
    """ Configures a chunk. """
    # Create lookup table for filepaths
    filepaths = dict([(path.name, path) for path in filepaths])

    image_file_groups: List[OrderedDict[str, Path]] = list()

    for index in references:
        fields = references[index]
        # master = 

        # Get image file paths
        left_filename = references["stereo_left_filename"][index]
        right_filename = references["stereo_right_filename"][index]

        if not left_filename in filepaths:
            logger.warning(f"could not find file: {left_filename}")
            continue
        
        if not right_filename in filepaths:
            logger.warning(f"could not find file: {right_filename}")
            continue
        
        file_group = OrderedDict()
        file_group["stereo_left"] = filepaths[left_filename]
        file_group["stereo_right"] = filepaths[right_filename]
        
        image_file_groups.append(file_group)

    add_image_groups_to_chunk(chunk, image_file_groups)

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

    # ---------------------------
    # ---- Search strategy ------
    # ---------------------------

    # Image search
    image_files = find_files_with_extension(
        arguments.images,
        extensions = [".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    logger.info(f"Found {len(image_files)} image files.")

    # ---------------------------
    # ---- Grouping strategy ----
    # ---------------------------

    # TODO: Load group keys from configuration

    # Get file groups from references
    target_files: Table = create_target_images_from_reference(
        references,
        group_keys = ["stereo_left_filename", "stereo_right_filename"],
    )

    # TODO: Match image groups with image files

    # Create chunk
    datetime = get_time_string("YYYYMMDD_hhmmss")
    chunk = create_chunk(document, f"{datetime}_add_chunk_script")
   
    # TODO: Configure chunk with images and references
    configure_chunk(
        chunk, 
        references, 
        image_groups = image_groups,
        image_files = image_files,
    )
   
    # Save document
    save_document(document, arguments.document)

if __name__ == "__main__":
    main()
