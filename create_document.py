""" Entry point for the package. """
from pathlib import Path
from typing import Dict

from loguru import logger
from result import Ok, Err, Result

from benthoscan.core.filesystem import list_directory
from benthoscan.core.io import read_csv, read_config
from benthoscan.core.utils import ArgumentParser, Namespace, get_time_string

from benthoscan.reconstruction.chunk import add_image_groups_to_chunk
from benthoscan.reconstruction.document import create_document, save_document

def validate_arguments(arguments: Namespace) -> Result[Namespace, str]:
    """ Validates the provided command line arguments. """
    if arguments.document.exists():
        return Err(f"document already exists: {arguments.document}")
    return Ok(arguments)

def main():
    """ Executed when the script is invoked. """
    parser = ArgumentParser()
    parser.add_argument("document",
        type = Path,
        help = "document path"
    )

    result: Result[Namespace, str] = validate_arguments(parser.parse_args())
    match result:
        case Err(message):
            logger.error(f"invalid arguments: {message}")
        case Ok(arguments):
            # Create new document and save to file
            document: Document = create_document()
            save_document(document, arguments.document)

if __name__ == "__main__":
    main()
