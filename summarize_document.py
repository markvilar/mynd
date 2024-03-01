""" Entry point for the package. """
from argparse import ArgumentParser, Namespace
from pathlib import Path

from loguru import logger
from result import Ok, Err, Result

from benthoscan.reconstruction.document import load_document
from benthoscan.reconstruction.summary import summarize_chunk, summarize_sensor

def validate_arguments(arguments: Namespace) -> Result[Namespace, str]:
    """ Validates the provided command line arguments. """
    if not arguments.document.exists():
        return Err(f"document file does not exist: {arguments.document}")
    return Ok(arguments)

def main():
    """ Executed when the script is invoked. """
    parser = ArgumentParser()
    parser.add_argument("document",
        type = Path,
        help = "metashape document path"
    )

    validation: Result[Namespace, str] = validate_arguments(parser.parse_args())
    if validation.is_err():
        logger.error(f"argument validation error: {validation.unwrap()}")

    arguments = validation.unwrap()

    # Load document
    document: Document = load_document(arguments.document)
   
    # Create summaries
    for chunk in document.chunks:
        summarize_chunk(chunk, logger.info)

        for sensor in chunk.sensors:
            summarize_sensor(sensor, logger.info)

if __name__ == "__main__":
    main()
