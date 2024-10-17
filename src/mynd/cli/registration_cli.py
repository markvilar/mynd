"""Module for invoking registration tasks through the command-line interface."""

from pathlib import Path

import click

from ..backend import metashape as backend
from ..io import read_config


@click.group()
def registration() -> None:
    """Group for registration commands invoked through the command-line interface."""
    pass


@registration.command()
@click.argument("project", type=click.Path())
@click.argument("processors", type=click.Path())
@click.option("--reference", type=str, help="reference group")
def register(project: click.Path, processors: click.Path) -> None:
    """Register groups of cameras to each other."""

    backend.load_project(Path(project))
    processors: dict = read_config(Path(processors))

    raise NotImplementedError("register is not implemented")
