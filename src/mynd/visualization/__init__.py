"""Package with visualization functionality including plotting, and 2D/3D rendering."""

from .geometry_renderers import (
    visualize_registration,
    visualize_registration_batch,
)

from .geometry_plotting import (
    create_subplots,
    trace_registration_result,
)

from .image_renderers import (
    WindowHandle,
    TrackbarData,
    create_window,
    render_image,
    destroy_window,
    destroy_all_windows,
    wait_key_input,
    StereoWindows,
    create_stereo_windows,
    render_stereo_geometry,
    create_stereo_geometry_color_image,
)


__all__ = [
    "visualize_registration",
    "visualize_registration_batch",
    "create_subplots",
    "trace_registration_result",
    "WindowHandle",
    "TrackbarData",
    "create_window",
    "render_image",
    "destroy_window",
    "destroy_all_windows",
    "wait_key_input",
    "StereoWindows",
    "create_stereo_windows",
    "render_stereo_geometry",
    "create_stereo_geometry_color_image",
]
