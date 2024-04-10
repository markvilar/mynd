""" Entry point for the package. """

from argparse import ArgumentParser, Namespace
from pathlib import Path

from loguru import logger
from result import Ok, Err, Result

from benthoscan.io import write_dict_to_file
from benthoscan.project import load_document
from benthoscan.project.summary import (
    summarize_chunk,
    summarize_sensor,
    summarize_camera,
)
from benthoscan.project.json_converters import convert_camera_to_json


def validate_arguments(arguments: Namespace) -> Result[Namespace, str]:
    """Validates the provided command line arguments."""
    if not arguments.document.exists():
        return Err(f"document file does not exist: {arguments.document}")
    return Ok(arguments)


def main():
    """Executed when the script is invoked."""
    parser = ArgumentParser()
    parser.add_argument("document", type=Path, help="metashape document path")

    validation: Result[Namespace, str] = validate_arguments(parser.parse_args())
    if validation.is_err():
        logger.error(f"argument validation error: {validation.unwrap()}")

    arguments = validation.unwrap()

    # Load document
    result: Result[Document, str] = load_document(arguments.document)
    document = result.unwrap()

    # Create summaries
    for index, chunk in enumerate(document.chunks):
        summarize_chunk(chunk, logger.info)

        logger.info("\n")
        logger.info(f"Cameras:       {len(chunk.cameras)}")
        logger.info(f"Trans. scale:  {str(chunk.transform.scale)}")
        logger.info(f"Trans. trans.: {str(chunk.transform.translation)}")
        logger.info(f"Trans. rot.:   {str(chunk.transform.rotation)}")
        logger.info("\n")

        camera_data = convert_camera_to_json(
            chunk.cameras[0], 
        )
       
        path = write_dict_to_file(
            camera_data, 
            Path(f"/home/martin/data/{index}_camera_data.json")
        ).unwrap()

        """
        for camera in chunk.cameras:
            logger.info(f"\n\n")
            summarize_camera(camera, logger.info)

        for sensor in chunk.sensors:
            logger.info(f"\n\n")
            summarize_sensor(sensor, logger.info)
        """


if __name__ == "__main__":
    main()
