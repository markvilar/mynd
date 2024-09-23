"""Module for camera related CLI functionality."""

import click


@click.group()
@click.pass_context
def camera_cli(context: click.Context) -> None:
    """CLI for camera specific tasks."""
    context.ensure_object(dict)


@camera_cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("destination", type=click.Path())
@click.argument("group", type=str)
@click.option("--stereo", is_flag=True, show_default=True, default=False, help="Export stereo geometry")
@click.option("--images", is_flag=True, show_default=True, default=False, help="Export image groups")
def export_cameras(source: str, destination: str) -> None:
    """Exports camera data from the backend."""

    # TODO: Set up H5 database for camera data
    # TODO: Add export camera task

    # NOTE: Basic export setup is to export basic camera data (references, attributes, sensors / calibrations)
    # TODO: Add option to export stereo calibrations
    # TODO: Add option to export images (range and normal maps)

    raise NotImplementedError("export_cameras is not implemented")
