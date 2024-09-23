"""Module for invoking reconstruction tasks through the command-line interface."""

from pathlib import Path

import click

from ..backend import metashape as backend
from ..io import read_config


@click.group()
def reconstruction() -> None:
    """Command-line interface to reconstruction task for the backend."""
    pass


@reconstruction.command()
@click.argument("project", type=click.Path())
@click.argument("processors", type=click.Path())
def reconstruct(project: click.Path, processors: click.Path) -> None:
    """Reconstruct geometry from groups of cameras."""

    backend.load_project(Path(project))
    processors: dict = read_config(Path(processors))

    raise NotImplementedError("reconstruct is not implemented")
