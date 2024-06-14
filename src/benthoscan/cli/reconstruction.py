"""Module for the reconstruction task entrypoint."""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from result import Ok, Err, Result

from benthoscan.io import read_toml
from benthoscan.project import Document, load_document, save_document
from benthoscan.runtime import Command
from benthoscan.utils.log import logger

from benthoscan.tasks.reconstruction.config_types import ReconstructionConfig
from benthoscan.tasks.reconstruction.worker import execute_reconstruction_task


def parse_task_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """TODO"""
    parser = ArgumentParser()

    parser.add_argument("document", type=Path, help="document path")
    parser.add_argument("processors", type=Path, help="reconstruction processors [sparse/dense]")
    parser.add_argument("--select", type=str, nargs="+", help="")
    parser.add_argument(
        "--overwrite", action=BooleanOptionalAction, help="overwrite data products"
    )

    namespace = parser.parse_args(arguments)

    if not namespace:
        return Err(f"failed to parse arguments: {arguments}")

    return Ok(namespace)


def configure_reconstruction_task(
    document_path: Path, 
    processor_path: Path, 
    chunk_selection: list[str]
) -> ReconstructionConfig:
    """"""

    document: Document = load_document(document_path).unwrap()
    processors: dict = read_toml(processor_path).unwrap()
    
    return ReconstructionConfig(
        document = document,
        target_labels = chunk_selection,
        processors = processors,
    )

def on_task_success(config) -> None:
    """TODO"""
    filepath: Path = Path(config.document.path)
    output_path: Path = filepath.parent / f"{filepath.stem}_recpipe.psz"
    
    match save_document(config.document, output_path):
        case Ok(path):
            logger.info(f"saved document: {output_path}")
        case Err(error):
            logger.error(f"failed to save document: {error}")
        case _:
            logger.info(f"unknown save result")


def on_task_failure(config: ReconstructionConfig, error: str) -> None:
    """TODO"""
    logger.error(f"reconstruction task failed")


def invoke_reconstruct_task(command: Command) -> None:
    """TODO"""

    namespace: Namespace = parse_task_arguments(command.arguments).unwrap()

    config: ReconstructionConfig = configure_reconstruction_task(
        namespace.document,
        namespace.processors,
        namespace.select
    )

    result: Result[None, str] = execute_reconstruction_task(config)

    match result:
        case Ok(None):
            on_task_success(config)
        case Err(error):
            on_task_failure(config, error)
