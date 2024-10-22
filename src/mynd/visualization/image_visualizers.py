"""Module for image visualization functionality."""

from collections.abc import Callable
from typing import NamedTuple, Optional

import cv2
import numpy as np


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


def create_image_visualizer(
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


def render_image(window: WindowHandle, values: np.ndarray) -> None:
    """Renders an array of values into an image."""
    cv2.imshow(window.name, values)


def destroy_window(window: WindowHandle) -> None:
    """Destroys a window."""
    cv2.destroyWindow(window.name)


def destroy_all_windows() -> None:
    """Destroys all the windows."""
    cv2.destroyAllWindows()
