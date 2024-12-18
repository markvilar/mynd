"""Module for running backend instances."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from mynd.utils.result import Ok, Err

# NOTE: Temporary - design mechanism to switch backend
from mynd.backend import metashape as backend


router = APIRouter()


@router.post("/project", tags=["project"])
def load_project(url: str | Path) -> dict:
    match backend.load_project(url):
        case Ok(url):
            return {"url": url, "message": "loaded project successfully"}
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@router.get("/project", tags=["project"])
def get_project_url() -> dict:
    """Returns the URL of the currently loaded backend project."""
    match backend.get_project_url():
        case Ok(url):
            return {"url": url}
        case Err(message):
            raise HTTPException(status_code=404, detail=message)
