"""TODO"""

from .setup import ProjectSetupData


def setup_project(project: ProjectSetupData) -> None:
    """"""

    document: Result[Document, str] = project.document_factory()

    for chunk_data in project.chunks:
        chunk: Result[Chunk, str] = project.chunk_factory(chunk_data.name)

        chunk_data.image_registry
        chunk_data.reference_registry
        
        cameras: list[Camera] = chunk_data.camera_factory()
