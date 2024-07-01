"""Module for various point cloud visualization methods."""

import copy

import numpy as np
import open3d

from .point_cloud_types import PointCloud


def draw_registration_result(
    source: PointCloud,
    target: PointCloud,
    transformation: np.ndarray,
    title: str = "Visualization",
):
    """TODO"""

    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    if transformation is not None:
        source_temp.transform(transformation)

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=title)
    vis.add_geometry(source_temp)
    vis.add_geometry(target_temp)
    vis.run()
    vis.destroy_window()
