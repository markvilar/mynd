"""Module for geometric image transformations."""

from dataclasses import dataclass
from typing import NamedTuple, Optional, Self

import cv2
import numpy as np

from ..data.image import Image


@dataclass
class PixelMap:
    """Class representing a pixel map. The pixel map data is an
    array of size HxWx2 with the X and Y pixel maps respectively."""
    
    data: np.ndarray

    def __post_init__(self: Self) -> None:
        """Validates the pixel map."""
        assert self.data.ndim == 3
        assert self.data.shape[2] == 2

    @property
    def height(self: Self) -> int:
        """Returns the height of the pixel map."""
        return self.data.shape[0]
        
    @property
    def width(self: Self) -> int:
        """Returns the width of the pixel map."""
        return self.data.shape[1]

    @property
    def shape(self: Self) -> tuple[int, int, int]:
        """Returns the shape of the pixel map."""
        return self.data.shape

    @property
    def ndim(self: Self) -> int:
        """Returns the dimension count of the pixel map."""
        return self.data.ndim
    
    @property
    def x(self: Self) -> np.ndarray:
        """Returns the x component of the pixel map."""
        return self.data[:, :, 0]

    @property
    def y(self: Self) -> np.ndarray:
        """Returns the y component of the pixel map."""
        return self.data[:, :, 1] 

    def to_array(self: Self) -> np.ndarray:
        """Returns the pixel map as an array."""
        return self.data.copy()
    

def compute_pixel_map(
    camera_matrix: np.ndarray, 
    distortion: np.ndarray, 
    rotation: np.ndarray,
    new_camera_matrix: np.ndarray,
    desired_resolution: tuple[int, int],
) -> PixelMap:
    """Computes a pixel map that maps the image as seen by original camera matrix,
    to an image seen by the new camera matrix."""

    map_components: tuple[np.ndarray, np.ndarray] = cv2.initUndistortRectifyMap(
        camera_matrix,
        distortion,
        rotation,
        new_camera_matrix,
        desired_resolution,
        cv2.CV_32FC1,
    )

    return PixelMap(np.stack((map_components[0], map_components[1]), axis=-1))


def invert_pixel_map(pixel_map: PixelMap, iterations: int=20, step_size: float=0.5) -> PixelMap:
    """Computes the inverse of a pixel map using iteration. The function
    takes a HxWx2 array representing a map from indices to subpixel index,
    and returns a HxWx2 array representing the inverse map."""
    
    height, width = pixel_map.shape[:2]

    I = np.zeros_like(pixel_map.data)
    I[:,:,1], I[:,:,0] = np.indices((height, width)) # identity map
    inverse_map_data: np.ndarray = np.copy(I)
    
    for index in range(iterations):
        correction: np.ndarray = I - cv2.remap(
            src=pixel_map.data, 
            map1=inverse_map_data, 
            map2=None,
            borderMode = cv2.BORDER_DEFAULT,
            interpolation=cv2.INTER_LINEAR,
        )
        inverse_map_data += correction * step_size

    return PixelMap(inverse_map_data)


def remap_image_pixels(
    image: Image, 
    pixel_map: PixelMap, 
    border_mode: int=cv2.BORDER_CONSTANT, 
    interpolation: int=cv2.INTER_LINEAR,
) -> Image:
    """Applies a pixel map to the pixels of the image."""
    mapped: np.ndarray = cv2.remap(
        src=image.to_array(),
        map1=pixel_map.to_array(),
        map2=None,
        borderMode=border_mode,
        interpolation=interpolation,
    )
    return Image(data=mapped, format=image.format, label=image.label)


class ImageCorners(NamedTuple):
    """Class representing image corners."""

    top_left: tuple[float, float]  # corners[0,0] = [0,0]
    top_right: tuple[float, float]  # corners[1,0] = [dims[0]-1,0]
    bottom_right: tuple[float, float]  # corners[2,0] = [dims[0]-1,dims[1]-1]
    bottom_left: tuple[float, float]  # corners[3,0] = [0, dims[1]-1]

    @property
    def min(self) -> tuple[float, float]:
        """Returns the minimum x- and y-coordinate of the image corners."""
        minx: float = min(self.top_left[0], self.top_right[0], self.bottom_right[0], self.bottom_left[0])
        miny: float = min(self.top_left[1], self.top_right[1], self.bottom_right[1], self.bottom_left[1])
        return (minx, miny)
    
    @property
    def max(self) -> tuple[float, float]:
        """Returns the maximum x- and y-coordinate of the image corners."""
        maxx: float = max(self.top_left[0], self.top_right[0], self.bottom_right[0], self.bottom_left[0])
        maxy: float = max(self.top_left[1], self.top_right[1], self.bottom_right[1], self.bottom_left[1])
        return (maxx, maxy)


def get_image_corners(
    homography: np.ndarray,
    camera_matrix: np.ndarray,
    dimensions: tuple[int, int],
    distortion: Optional[np.ndarray] = None,
) -> ImageCorners:
    """Estimates updated image corners locations based on a combined homography
    and undistortion transformation."""
    
    if distortion is None:
        distortion = np.zeros(5)

    # Set image corners in the form requested by cv2.undistortPoints
    corners = np.zeros((4, 1, 2), dtype=np.float32)
    
    # Initialize corners in order: top left, top right, bottom right, bottom left
    corners[0, 0] = [0, 0]
    corners[1, 0] = [dimensions[0] - 1, 0]
    corners[2, 0] = [dimensions[0] - 1, dimensions[1] - 1]
    corners[3, 0] = [0, dimensions[1] - 1]

    undistorted_corners: np.ndarray = cv2.undistortPoints(
        corners, camera_matrix, distortion, R=homography.dot(camera_matrix)
    )

    undistorted_corners: list[tuple] = [(x, y) for x, y in np.squeeze(undistorted_corners)]
    
    return ImageCorners(*undistorted_corners)

    """
        top_left=undistorted_corners[0],
        top_right=undistorted_corners[1],
        bottom_right=undistorted_corners[2],
        bottom_left=undistorted_corners[3],
    )
    """
