"""Main entrypoint for the command-line interface."""

import click

from .camera_cli import camera_cli
from .ingest_cli import ingestion
from .reconstruction_cli import reconstruction
from .registration_cli import registration


# Create the main CLI as a collection of task specific CLIs
main_cli = click.CommandCollection(
    sources=[camera_cli, ingestion, reconstruction, registration]
)


def main():
    """Runs the command-line interface."""

    main_cli()


if __name__ == "__main__":
    main()
