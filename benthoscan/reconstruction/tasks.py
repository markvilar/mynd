""" Metashape align functions. """

import Metashape

"""
chunk.matchPhotos(downscale=1, generic_preselection=True, reference_preselection=False)
chunk.alignCameras()
chunk.buildDepthMaps(downscale=4, 
    filter_mode=Metashape.AggressiveFiltering
)
chunk.buildModel(source_data=Metashape.DepthMapsData, surface_type=Metashape.Arbitrary, 
    interpolation=Metashape.EnabledInterpolation
)
chunk.buildUV(mapping_mode=Metashape.GenericMapping)
chunk.buildTexture(blending_mode=Metashape.MosaicBlending, texture_size=4096)
doc.save()
"""

def match_chunk_images(chunk: Metashape.Chunk):
    """ Matches the photos for the given chunk. """
    chunk.matchPhotos(
        downscale=1, 
        generic_preselection=True, 
        reference_preselection=False
    )

def align_chunk_cameras(chunk: Metashape.Chunk) -> None:
    """ Aligns the cameras in a chunk. """
    chunk.alignCameras()

def build_depth_maps(chunk: Metashape.Chunk) -> None:
    """ Builds depth maps for the given chunk. """
    chunk.buildDepthMaps(
        downscale=4, 
        filter_mode=Metashape.AggressiveFiltering
    )

def build_dense_point_cloud(chunk: Metashape.Chunk) -> None:
    """ Builds a dense point cloud model for the given chunk. """
    chunk.buildModel(
        source_data=Metashape.DepthMapsData, 
        surface_type=Metashape.Arbitrary, 
        interpolation=Metashape.EnabledInterpolation
    )

def build_coordinate_map(chunk: Metashape.Chunk) -> None:
    """ Builds a coordinate map for the given chunk. """
    chunk.buildUV(mapping_mode=Metashape.GenericMapping)

def build_texture(chunk: Metashape.Chunk) -> None:
    """ Builds a model texture for the given chunk. """
    chunk.buildTexture(
        blending_mode=Metashape.MosaicBlending, 
        texture_size=4096
    )

