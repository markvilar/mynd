""" Entry point for the package. """

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from loguru import logger
from result import Ok, Err, Result

from benthoscan.reconstruction.document import create_document, save_document


def validate_arguments(arguments: Namespace) -> Result[Namespace, str]:
    """Validates the provided command line arguments."""
    if not arguments.overwrite and arguments.document.exists():
        return Err(f"document already exists: {arguments.document}")
    if not arguments.document.suffix in [".psx", ".psz"]:
        return Err(f"invalid document extension: {arguments.document.suffix}")

    return Ok(arguments)


def main():
    """Executed when the script is invoked."""
    parser = ArgumentParser("creates a Metashape document at the given path")
    parser.add_argument("document", type=Path, help="document path")
    parser.add_argument("--overwrite", action=BooleanOptionalAction)

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
