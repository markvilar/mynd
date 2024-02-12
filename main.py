""" Entry point for the package. """
from pathlib import Path

from loguru import logger

from benthoscan.core.utils import ArgumentParser, Namespace

from benthoscan.reconstruction.chunk import add_image_groups_to_chunk
from benthoscan.reconstruction.document import create_document, create_chunk

def main():
    """ Executed when the script is invoked. """
    parser = ArgumentParser()
    parser.add_argument("images",
        type = Path,
        help = "image directory path"
    )
    parser.add_argument("cameras",
        type = Path,
        help = "camera reference path"
    )

    arguments: Namespace = parser.parse_args()

    logger.info(f"images:  {arguments.images}")
    logger.info(f"cameras: {arguments.cameras}")

    filegroups = [2]*(10 // 2)

    logger.info(filegroups)

    # TODO: Create document
    document: Document = create_document(Path("/home/martin/test/document.psz"))
    
    # TODO: Create chunk
    chunk = create_chunk(document)
    add_image_groups_to_chunk(chunk, list())

    # TODO: Add chunks to document - images, references


if __name__ == "__main__":
    main()
