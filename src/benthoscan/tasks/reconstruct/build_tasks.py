"""Module with reconstruction processes. """

import Metashape

from benthoscan.project import Chunk


def match_chunk_images(chunk: Chunk):
    """Matches the photos for the given chunk."""
    chunk.matchPhotos(
        downscale=1, generic_preselection=True, reference_preselection=False
    )


def align_chunk_cameras(chunk: Chunk) -> None:
    """Aligns the cameras in a chunk."""
    chunk.alignCameras()


def build_depth_maps(chunk: Chunk) -> None:
    """Builds depth maps for the given chunk."""
    chunk.buildDepthMaps(downscale=4, filter_mode=Metashape.AggressiveFiltering)


def build_dense_point_cloud(chunk: Chunk) -> None:
    """Builds a dense point cloud model for the given chunk."""
    chunk.buildModel(
        source_data=Metashape.DepthMapsData,
        surface_type=Metashape.Arbitrary,
        interpolation=Metashape.EnabledInterpolation,
    )


def build_coordinate_map(chunk: Chunk) -> None:
    """Builds a coordinate map for the given chunk."""
    chunk.buildUV(mapping_mode=Metashape.GenericMapping)


def build_texture(chunk: Chunk) -> None:
    """Builds a model texture for the given chunk."""
    # TODO: Look for option to only use left cameras.
    chunk.buildTexture(blending_mode=Metashape.MosaicBlending, texture_size=4096)
