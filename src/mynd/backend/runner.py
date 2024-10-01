"""Module for running backend instances."""

from pathlib import Path

import click
import uvicorn

from fastapi import FastAPI, HTTPException

import mynd.backend.metashape as backend

from mynd.collections import CameraGroup
from mynd.utils.log import logger
from mynd.utils.result import Ok, Err


app = FastAPI()


GroupID = CameraGroup.Identifier


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.put("/project")
async def load_project(url: str | Path) -> dict:
    match backend.load_project(url):
        case Ok(url):
            return {"url": url, "message": "loaded project successfully"}
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@app.get("/project")
async def get_project_url() -> dict:
    """Returns the URL of the currently loaded backend project."""
    match backend.get_project_url():
        case Ok(url):
            return {"url": url}
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@app.get("/group_identifiers", response_model=list[CameraGroup.Identifier])
async def get_group_identifiers() -> dict:
    """Returns the group identifiers in the currently loaded backend project."""
    match backend.get_group_identifiers():
        case Ok(identifiers):
            return identifiers
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@app.get("/cameras/attributes", response_model=CameraGroup.Attributes)
async def get_camera_attributes(identifier: GroupID) -> CameraGroup.Attributes:
    """Gets primary camera data, such as keys, labels, images, and sensor keys."""
    match backend.get_camera_attributes(identifier):
        case Ok(attributes):
            return attributes
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
