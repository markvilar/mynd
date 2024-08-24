"""Module for the reconstruction task entrypoint."""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path

from ..io import read_config
from ..runtime import Command
from ..tasks.reconstruction import ReconstructionConfig
from ..tasks.reconstruction import execute_reconstruction_task
from ..utils.result import Ok, Err, Result


def parse_task_arguments(arguments: list[str]) -> Result[Namespace, str]:
    """TODO"""
    parser = ArgumentParser()

    parser.add_argument("document", type=Path, help="document path")
    parser.add_argument(
        "processors", type=Path, help="reconstruction processors [sparse/dense]"
    )
    parser.add_argument("--select", type=str, nargs="+", help="")
    parser.add_argument(
        "--overwrite", action=BooleanOptionalAction, help="overwrite data products"
    )

    namespace = parser.parse_args(arguments)

    if not namespace:
        return Err(f"failed to parse arguments: {arguments}")

    return Ok(namespace)


def configure_reconstruction_task(
    document_path: Path, processor_path: Path, chunk_selection: list[str]
) -> ReconstructionConfig:
    """Creates a reconstruction task configuration from the given arguments."""

    processors: dict = read_config(processor_path).unwrap()

    return ReconstructionConfig(
        document_path=document_path,
        target_labels=chunk_selection,
        processors=processors,
    )


def on_task_success(config: ReconstructionConfig) -> None:
    """TODO"""
    raise NotImplementedError("on_task_success is not implemented")


def on_task_failure(config: ReconstructionConfig, error: str) -> None:
    """TODO"""
    raise NotImplementedError("on_task_failure is not implemented")


def invoke_reconstruct_task(command: Command) -> None:
    """TODO"""

    namespace: Namespace = parse_task_arguments(command.arguments).unwrap()

    config: ReconstructionConfig = configure_reconstruction_task(
        namespace.document, namespace.processors, namespace.select
    )

    result: Result[None, str] = execute_reconstruction_task(config)

    match result:
        case Ok(None):
            on_task_success(config)
        case Err(error):
            on_task_failure(config, error)
