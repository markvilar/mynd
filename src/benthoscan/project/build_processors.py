"""Module for sparse and dense reconstruction processors."""

from functools import partial
from typing import Callable

import Metashape

from result import Ok, Err, Result

from benthoscan.utils.log import logger
from benthoscan.utils.redirect import stdout_redirected


"""
Sparse processors:
 - match images
 - align cameras
 - optimize cameras
"""

ProgressCallback = Callable[[float], None]


def build_sparse_processor(config: dict) -> Result[Callable, str]:
    """TODO"""

    processor_type: str = config["process"]
    enabled: bool = config["enabled"]
    parameters: dict = config["parameters"]

    match processor_type:
        case "match_images":
            return Ok(partial(match_images, parameters=parameters))
        case "align_cameras":
            return Ok(partial(align_cameras, parameters=parameters))
        case "optimize_cameras":
            return Ok(partial(optimize_cameras, parameters=parameters))
        case _:
            return Err(f"invalid processor type: {processor_type}")


def match_images(
    chunk: Metashape.Chunk, 
    progress_fun: ProgressCallback, 
    parameters: dict
) -> Result[None, str]:
    """Matches the images in the chunk."""
    # TODO: Map reference preselection mode to Metashapes options
    with stdout_redirected():
        try:
            chunk.matchPhotos(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)

    return Ok(None)


def align_cameras(
    chunk: Metashape.Chunk, 
    progress_fun: ProgressCallback, 
    parameters: dict
) -> Result[None, str]:
    """Aligns the cameras in the chunk."""
    with stdout_redirected():
        try:
            chunk.alignCameras(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)
    
    return Ok(None)


def optimize_cameras(
    chunk: Metashape.Chunk, 
    progress_fun: ProgressCallback, 
    parameters: dict
) -> Result[None, str]:
    """Optimizes the calibration and camera poses in the chunk."""
    with stdout_redirected():
        try:
            chunk.optimizeCameras(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)
    
    return Ok(None)


SPARSE_PROCESSORS = {
    "match_images": match_images,
    "align_cameras": align_cameras,
    "optimize_cameras": optimize_cameras,
}


"""
Dense processors:
 - build_depth_maps
 - build_point_cloud
 - build_mesh
 - build_coordinate_map
 - build_texture
"""


def build_dense_processor(config: dict) -> Result[Callable, str]:
    """TODO"""

    processor: str = config["process"]
    enabled: bool = config["enabled"]
    parameters: dict = config["parameters"]

    match processor:
        case "build_depth_maps":
            return Ok(partial(build_depth_maps, parameters=parameters))
        case "build_point_cloud":
            return Ok(partial(build_point_cloud, parameters=parameters))
        case "build_texture":
            return Ok(partial(build_texture, parameters=parameters))
        case _:
            return Err(f"invalid processor: {processor}")


def build_depth_maps(
    chunk: Metashape.Chunk, 
    progress_fun: ProgressCallback, 
    parameters: dict,
) -> Result[None, str]:
    """Builds depth maps for the given chunk."""
    with stdout_redirected():
        try:
            chunk.buildDepthMaps(
                **parameters,
                filter_mode=Metashape.MildFiltering,
                progress=progress_fun,
            )
        except BaseException as error:
            return Err(error)
    
    return Ok(None)


def build_point_cloud(
    chunk: Metashape.Chunk,
    progress_fun: ProgressCallback, 
    parameters: dict,
) -> Result[None, str]:
    """Builds a dense point cloud for the given chunk."""
    with stdout_redirected():
        try:
            chunk.buildPointCloud(
                **parameters,
                progress = progress_fun,
            )
        except BaseException as error:
            return Err(error)
    
    return Ok(None)


def build_mesh(
    chunk: Metashape.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback, 
) -> Result[None, str]:
    """Builds a mesh model for the given chunk."""
    # TODO: Add mapping for Metashape internal argument types
    with stdout_redirected():
        try:
            chunk.buildModel(
                source_data=Metashape.DepthMapsData,
                surface_type=Metashape.Arbitrary,
                interpolation=Metashape.EnabledInterpolation,
                progress = progress_fun,
            )
        except BaseException as error:
            return Err(error)

    return Ok(None)
    

def build_coordinate_map(
    chunk: Metashape.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback=None, 
) -> Result[None, str]:
    """Builds a coordinate map for the given chunk."""

    # TODO: Add conversion support for the following type: Metashape.GenericMapping, 

    with stdout_redirected():
        try:
            chunk.buildUV(
                **parameters,
                progress=progress_fun,
            )
        except BaseException as error:
            return Err(error)

    return Ok(None)


def build_texture(
    chunk: Metashape.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback=None, 
) -> Result[None, str]:
    """Builds a model texture for the given chunk."""
    
    # TODO: Look for option to only use left cameras.
    # TODO: Add conversion support for the following type: Metashape.MosaicBlending, 

    with stdout_redirected():
        try:
            chunk.buildTexture(
                **parameters,
                progress=progress_fun,
            )
        except BaseException as error:
            return Err(error)

    return Ok(None)


DENSE_PROCESSORS = {
    "build_depth_maps": build_depth_maps,
    "build_point_cloud": build_point_cloud,
    "build_mesh": build_mesh,
    "build_coordinate_map": build_coordinate_map,
    "build_texture": build_texture,
}
