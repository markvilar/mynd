"""Module for functionality related to range maps. Currently the module includes functionality
for computing range from disparity, 3D points from range, and normal maps from range maps."""

import warnings ; warnings.warn = lambda *args,**kwargs: None

import numpy as np
import torch
import kornia.geometry.depth as kgd




def compute_range_from_disparity(
    disparity: np.ndarray, 
    baseline: float, 
    focal_length: float,
) -> np.ndarray:
    """Computes a range map from the given disparity map and camera matrix. Returns the 
    range map as a HxW array with float32 values."""

    range_tensor: torch.Tensor = kgd.depth_from_disparity(
        disparity=disparity, 
        baseline=baseline, 
        focal=focal_length,
    )

    range_map: np.ndarray = np.squeeze(range_tensor.numpy()).transpose((1, 2, 0)).astype(np.float32)
    return range_map


def compute_points_from_range(
    range_map: np.ndarray, 
    camera_matrix: np.ndarray, 
    normalize_points: bool=False
) -> np.ndarray:
    """Computes 3D points based on the given range map and camera matrix. Returns 
    the points as a HxWx3 array with float32 values."""
    
    range_tensor: torch.Tensor = _range_map_to_tensor(range_map)
    camera_tensor: torch.Tensor = _camera_matrix_to_tensor(camera_matrix)

    point_tensor: torch.Tensor = kgd.depth_to_3d_v2(
        depth=_range_map_to_tensor(range_map),
        camera_matrix=_camera_matrix_to_tensor(camera_matrix),
        normalize_points=normalize_points,
    )

    points: np.ndarray = np.squeeze(point_tensor.numpy()).transpose((1, 2, 0)).astype(np.float32)

    return points


def compute_normals_from_range(
    range_map: np.ndarray, 
    camera_matrix: np.ndarray, 
    flipped: bool=False,
    normalize_points: bool=False,
) -> np.ndarray:
    """Computes normal map based on the given range map and camera matrix. Returns 
    the normals as float32 unit vectors. If flipped is true, the normals are defined 
    with positive x-, y-, and z pointing right, down, and away as seen by the camera."""

    normal_tensor: torch.Tensor = kgd.depth_to_normals(
        depth=_range_map_to_tensor(range_map), 
        camera_matrix=_camera_matrix_to_tensor(camera_matrix), 
        normalize_points=normalize_points,
    )
    
    normals: np.ndarray = np.squeeze(normal_tensor.numpy()).transpose((1, 2, 0)).astype(np.float32)

    # Convert to unit vectors
    norms: np.ndarray = np.linalg.norm(normals, axis=2)

    NORM_THRESHOLD: float = 0.0000001
    invalid: np.ndarray = norms < NORM_THRESHOLD
    norms[invalid] = 1.0
    normals[invalid] = np.zeros(3)

    # Convert normals into unit vectors
    normals /= norms[:, :, np.newaxis]

    if flipped:
        normals: np.ndarray = -normals

    return normals


def _camera_matrix_to_tensor(camera_matrix: np.ndarray) -> torch.Tensor:
    """Converts a 3x3 camera matrix into a 1x3x3 torch tensor."""
    camera_matrix: np.ndarray = np.squeeze(camera_matrix)
    return torch.from_numpy(camera_matrix.copy()).view(1, 3, 3)


def _range_map_to_tensor(range_map: np.ndarray) -> torch.Tensor:
    """Converts a HxW range map into a 1x1xHxW torch tensor."""
    range_map: np.ndarray = np.squeeze(range_map)
    return torch.from_numpy(range_map.copy()).view(1, 1, range_map.shape[0], range_map.shape[1])
