"""Module for running backend instances."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException

from mynd.collections import CameraGroup
from mynd.utils.result import Ok, Err, Result

# NOTE: Temporary - design mechanism to switch backend
from mynd.backend import metashape as backend

router = APIRouter()


Label = str
Metadata = dict[str, Any]
GroupID = CameraGroup.Identifier


@router.get(
    "/group_identifiers",
    tags=["groups"],
    response_model=list[CameraGroup.Identifier],
)
def get_group_identifiers() -> dict:
    """Returns the group identifiers in the currently loaded backend project."""
    match backend.get_group_identifiers():
        case Ok(identifiers):
            return identifiers
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@router.get("/cameras/attributes", tags=["cameras"])
def get_camera_attributes(identifier: GroupID) -> CameraGroup.Attributes:
    """Gets primary camera data, such as keys, labels, images, and sensor keys."""
    match backend.camera_services.get_camera_attributes(identifier):
        case Ok(attributes):
            return attributes
        case Err(message):
            raise HTTPException(status_code=404, detail=message)


@router.post("/cameras/metadata", tags=["cameras"])
def update_camera_metadata(
    camera_metadata: dict[Label, Metadata],
    identifier: Optional[GroupID] = None,
) -> str:
    """TODO"""
    result: Result[dict, str] = backend.camera_services.update_camera_metadata(
        identifier,
        camera_metadata,
    )

    match result:
        case Ok(statistics):
            return statistics
        case Err(message):
            raise HTTPException(status_code=404, detail=message)
