"""TODO"""

from benthoscan.project import Document, Chunk, create_chunk

from .config_types import ProjectSetupData


def setup_project_data(project: ProjectSetupData) -> None:
    """TODO"""

    document: Document = project.document

    for chunk_data in project.chunks:
        chunk: Result[Chunk, str] = create_chunk(chunk_data.chunk_name)

        cameras: list[Camera] = chunk_data.cameras
        image_registry: Registry[str, Path] = chunk_data.image_registry
        reference_registry: Registry[str, object] = chunk_data.reference_registry
        
        cameras: list[Camera] = chunk_data.camera_factory()
