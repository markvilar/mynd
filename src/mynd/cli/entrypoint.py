"""Main entrypoint for the command-line interface."""

# TODO: Implement ingestion / reconstruction / registration CLIs
# from .ingestion import invoke_project_setup
# from .reconstruction import invoke_reconstruct_task
# from .registration import invoke_registration_task


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
