"""Module that implements the ingestion service for the Metashape backend."""

from pathlib import Path

import Metashape

from result import Ok, Err, Result

from ...project import ProjectData, DocumentOptions, CameraGroupData
from ...utils.log import logger

from .camera_helpers import add_camera_group, add_camera_references
from .project import load_document, create_document, save_document, create_chunk


def handle_document(options: DocumentOptions) -> Result[Metashape.Document, str]:
    """Creates a new or loads an existing document based on the options."""

    if options.create_new or not options.path.exists():
        document: Metashape.Document = create_document()
    else:
        result: Result[Metashape.Document, str] = load_document(options.path)

        if result.is_err():
            return result
        else:
            document = result.ok()

    return Ok(document)


CameraIngestResult = Result[None, str]


def ingest_camera_group(
    document: Metashape.Document,
    camera_group: CameraGroupData,
) -> CameraIngestResult:
    """Ingests camera data, i.e. photos, camera configuration, and references,
    in a Metashape chunk."""

    chunk: Metashape.Chunk = create_chunk(document, camera_group.name)

    # TODO: Move chunk and camera CRS to config
    chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
    chunk.camera_crs = Metashape.CoordinateSystem("EPSG::4326")

    # Add camera group to configure images and sensors
    results: list[Result[None, str]] = [
        add_camera_group(
            chunk,
            camera_group.cameras,
            camera_group.images,
        ),
        add_camera_references(
            chunk,
            camera_group.cameras,
            camera_group.references,
        ),
    ]

    for result in results:
        if result.is_err():
            return result

    return Ok(None)


def request_data_ingestion(project: ProjectData) -> Result[Path, str]:
    """Request a data ingestion for a given document."""

    result: Result[Metashape.Document, str] = handle_document(project.document_options)

    if result.is_err():
        return result

    document: Metashape.Document = result.ok()

    ingestions: dict[str, CameraIngestResult] = {
        group.name: ingest_camera_group(document, group)
        for group in project.camera_groups
    }

    for name, result in ingestions.items():
        match result:
            case Err(message):
                return Err(f"failed to ingest camera group '{name}': {message}")

    result: Result[Path, str] = save_document(
        document, path=project.document_options.path
    )
    return result
