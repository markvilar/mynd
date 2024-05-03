"""Module for task specific arguments."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from result import Ok, Err, Result


def create_argument_parser() -> ArgumentParser:
    """Creates a parser and adds arguments to it."""
    parser = ArgumentParser()
    parser.add_argument("document", type=Path, help="metashape document path")
    parser.add_argument("images", type=Path, help="image directory path")
    parser.add_argument("references", type=Path, help="camera reference path")
    parser.add_argument(
        "config",
        type=Path,
        help="configuration file path",
    )
    parser.add_argument(
        "name",
        type=str,
        help="chunk name",
    )
    return parser


def validate_arguments(arguments: Namespace) -> Result[Namespace, str]:
    """Validates the provided command line arguments."""
    if not arguments.document.exists():
        return Err(f"document file does not exist: {arguments.document}")
    if not arguments.images.exists():
        return Err(f"image directory does not exist: {arguments.images}")
    if not arguments.references.exists():
        return Err(f"camera file does not exist: {arguments.references}")
    if not arguments.config.exists():
        return Err(f"camera file does not exist: {arguments.config}")
    return Ok(arguments)
