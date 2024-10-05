"""Module for running backend instances."""

from fastapi import FastAPI

import click
import uvicorn

from ..utils.log import logger

from .routers import base, camera


app = FastAPI()
app.include_router(base.router)
app.include_router(camera.router)


@click.command()
@click.argument("host", type=str, default="localhost")
@click.argument("port", type=int, default=5000)
@click.option("--reload", is_flag=True, default=False)
def main(host: str, port: int, reload: bool) -> None:
    """Runs the backend instance."""
    logger.info(f"Running backend: host={host}, port={port}, reload={reload}")
    uvicorn.run("src.mynd.app.runner:app", host=host, port=port, reload=reload)
