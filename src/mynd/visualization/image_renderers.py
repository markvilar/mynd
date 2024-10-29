"""Module for image visualization functionality."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import NamedTuple, Optional

import cv2
import numpy as np

from mynd.geometry import StereoGeometry
from mynd.utils.key_codes import KeyCode


class WindowHandle(NamedTuple):
    """Class representing a window handle."""

    name: str
    width: int
    height: int


class TrackbarData(NamedTuple):
    """Class representing trackbar data."""

    name: str
    lower: int | float
    upper: int | float
    callback: Callable[[int | float], None]


def create_window(
    window_name: str = "Window",
    width: int = 800,
    height: int = 1200,
    track_bars: Optional[list[TrackbarData]] = None,
) -> WindowHandle:
    """Creates a window with optional track bars."""

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, width, height)

    if track_bars:
        for track_bar in track_bars:
            cv2.createTrackbar(
                track_bar.name,
                window_name,
                track_bar.lower,
                track_bar.upper,
                track_bar.callback,
            )

    return WindowHandle(name=window_name, width=width, height=height)


def wait_key_input(wait: int) -> KeyCode:
    """Waits for a keyboard input."""
    key: int = cv2.waitKey()
    try:
        key_code: KeyCode = KeyCode(key)
    except ValueError:
        key_code: KeyCode = KeyCode.NULL
    return key_code


def colorize_values(
    values: np.ndarray,
    lower: int | float,
    upper: int | float,
    flip: bool = False,
) -> np.ndarray:
    """Convert an array of values into a color map."""

    values[values > upper] = upper
    values[values < lower] = lower

    min_value: float = values.min()
    max_value: float = values.max()

    # TODO: Add non-linear scaling
    if flip:
        scale: int = -255
        offset: int = 255
    else:
        scale: int = 255
        offset: int = 0
    normalized: np.ndarray = (values - min_value) / (
        max_value - min_value
    ) * scale + offset
    normalized: np.ndarray = normalized.astype(np.uint8)
    normalized: np.ndarray = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
    return normalized.astype(np.uint8)


def render_image(window: WindowHandle, values: np.ndarray) -> None:
    """Renders an array of values into an image."""
    cv2.imshow(window.name, values)


@dataclass
class StereoWindows:
    """Class representing a collection of windows for rendering stereo data."""

    rectified_left: WindowHandle
    rectified_right: WindowHandle

    disparity_left: WindowHandle
    disparity_right: WindowHandle

    range_left: WindowHandle
    range_right: WindowHandle


def create_stereo_windows() -> StereoWindows:
    """Creates a collection of windows for rendering stereo geometries."""
    return StereoWindows(
        rectified_left=create_window("rectified_left", 680, 512),
        rectified_right=create_window("rectified_right", 680, 512),
        disparity_left=create_window("disparity_left", 680, 512),
        disparity_right=create_window("disparity_right", 680, 512),
        range_left=create_window("range_left", 680, 512),
        range_right=create_window("range_right", 680, 512),
    )


def render_stereo_geometry(
    windows: StereoWindows, geometry: StereoGeometry
) -> None:
    """Render a stereo geometry into a collection of windows."""

    # Colorize disparity maps
    disparity_left: np.ndarray = colorize_values(
        geometry.disparities.first, lower=0, upper=300
    )
    dispartiy_right: np.ndarray = colorize_values(
        geometry.disparities.second, lower=0, upper=300
    )

    # Colorize range maps
    range_left: np.ndarray = colorize_values(
        geometry.range_maps.first.to_array(), lower=0.0, upper=8.0, flip=True
    )
    range_right: np.ndarray = colorize_values(
        geometry.range_maps.second.to_array(), lower=0.0, upper=8.0, flip=True
    )

    # Render rectified images
    render_image(
        windows.rectified_left, geometry.rectified_images.first.to_array()
    )
    render_image(
        windows.rectified_right, geometry.rectified_images.second.to_array()
    )

    # Render disparity maps
    render_image(windows.disparity_left, disparity_left)
    render_image(windows.disparity_right, dispartiy_right)

    # Render range
    render_image(windows.range_left, range_left)
    render_image(windows.range_right, range_right)


def destroy_window(window: WindowHandle) -> None:
    """Destroys a window."""
    cv2.destroyWindow(window.name)


def destroy_all_windows() -> None:
    """Destroys all the windows."""
    cv2.destroyAllWindows()
