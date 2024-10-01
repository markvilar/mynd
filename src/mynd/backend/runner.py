"""Module for running backend instances."""

from pathlib import Path

import click
import uvicorn

from fastapi import FastAPI, HTTPException

import mynd.backend.metashape as backend

from mynd.api import CameraGroup
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
async def get_project_url() -> dict:
    """Returns the URL of the currently loaded backend project."""
    get_result: Result[str | Path] = backend.get_project_url()
    match get_result:
        case Ok(url):
            return {"url": url}
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@app.get("/group_identifiers", response_model=list[CameraGroup.Identifier])
async def get_group_identifiers() -> dict:
    """Returns the group identifiers in the currently loaded backend project."""
    get_identifier_result: Result[list[CameraGroup.Identifier], str] = (
        backend.get_group_identifiers()
    )
    match get_identifier_result:
        case Ok(identifiers):
            return identifiers
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@app.get(
    "/cameras/attributes",
    response_model=dict[CameraGroup.Identifier, CameraGroup.Attributes],
)
async def get_camera_attributes() -> dict:
    """Gets primary camera data, such as keys, labels, images, and sensor keys."""
    get_camera_result: Result[dict, str] = backend.get_camera_attributes()
    match get_camera_result:
        case Ok(groups):
            return groups
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@click.command()
@click.argument("host", type=str, default="0.0.0.0")
@click.argument("port", type=int, default=5000)
@click.option("--reload", is_flag=True, default=False)
def main(host: str, port: int, reload: bool) -> None:
    """Runs the backend instance."""
    logger.info(f"Running backend: host={host}, port={port}, reload={reload}")
    uvicorn.run(
        "src.mynd.backend.runner:app", host=host, port=port, reload=reload
    )
