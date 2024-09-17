"""Module that implements the ingestion service for the Metashape backend."""

from pathlib import Path

import Metashape as ms

from ....project import ProjectData, DocumentOptions, CameraGroupData
from ....utils.result import Ok, Err, Result

from ..ingest.ingest_helpers import add_camera_group
from ..project import load_document, create_document, save_document, create_chunk


def handle_document(options: DocumentOptions) -> Result[ms.Document, str]:
    """Creates a new or loads an existing document based on the options."""

    if options.create_new or not options.path.exists():
        document: ms.Document = create_document()
    else:
        result: Result[ms.Document, str] = load_document(options.path)

        if result.is_err():
            return result
        else:
            document = result.ok()

    return Ok(document)


CameraIngestResult = Result[None, str]


def ingest_camera_group(
    document: ms.Document,
    camera_group: CameraGroupData,
) -> CameraIngestResult:
    """Ingests camera data, i.e. photos, camera configuration, and references,
    in a Metashape chunk."""

    chunk: ms.Chunk = create_chunk(document, f"{camera_group.name}")

    # TODO: Add ingestion statistics
    add_camera_group(chunk, camera_group)

    return Ok(None)


def request_data_ingestion(project: ProjectData) -> Result[Path, str]:
    """Request a data ingestion for a given document."""

    result: Result[ms.Document, str] = handle_document(project.document_options)

    if result.is_err():
        return result

    document: ms.Document = result.ok()

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
