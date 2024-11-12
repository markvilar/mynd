"""Module for invoking registration tasks through the command-line interface."""

from pathlib import Path

import click

from .entrypoint import invoke_registration


@click.group()
def registration() -> None:
    """Group for registration commands invoked through the command-line interface."""
    pass


@registration.command()
@click.argument("source", type=Path)
@click.argument("destination", type=Path)
@click.argument("config", type=Path)
@click.argument("cache", type=Path)
@click.option("--reference", type=str, help="reference group label")
@click.option(
    "--vis", "visualize", is_flag=True, default=False, help="visualize results"
)
@click.option(
    "--force",
    "force_export",
    is_flag=True,
    default=False,
    help="force result saving",
)
def register(
    source: Path,
    destination: Path,
    config: Path,
    cache: Path,
    reference: str | None = None,
    visualize: bool = False,
    force_export: bool = False,
) -> None:
    """Register groups of cameras to each other."""

    assert source.exists(), f"file does not exist: {source}"
    assert (
        destination.parent.exists()
    ), f"directory does not exist: {destination.parent}"
    assert config.exists(), f"file does not exist: {config}"

    # Sanity check
    assert source != destination, "source and destination cannot be the same"

    invoke_registration(
        source, destination, config, cache, reference, visualize, force_export
    )
