"""Module for running backend instances."""

from pathlib import Path

import click
import uvicorn

from fastapi import FastAPI, HTTPException

import mynd.backends.metashape as backend

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.put("/project")
async def load_project(url: str | Path) -> None:
    load_result: Result[str, str] = backend.load_project(url)
    match load_result:
        case Ok(url):
            return {"url": url, "message": "loaded project successfully"}
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@app.get("/project")
async def get_project() -> dict:
    """Returns the URL of the currently loaded backend project."""
    get_result: Result[str | Path] = backend.get_project()
    match get_result:
        case Ok(url):
            return {"url": url}
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@app.get("/cameras")
async def get_cameras() -> dict:
    """Gets primary camera data, such as keys, labels, images, and sensor keys."""

    pass


@click.command()
@click.argument("host", type=str, default="0.0.0.0")
@click.argument("port", type=int, default=5000)
@click.option("--reload", type=bool, default=False)
def main(host: str, port: int, reload: bool) -> None:
    """Runs the backend instance."""
    logger.info(f"Running backend: host={host}, port={port}, reload={reload}")
    uvicorn.run("src.mynd.backends.runner:app", host=host, port=port, reload=reload)
