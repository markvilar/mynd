"""Module for IO functionality for images."""

from pathlib import Path
from typing import Optional

import imageio.v3 as iio
import numpy as np

from result import Ok, Err, Result


def write_image(
    uri: str | Path, 
    image: np.ndarray,
    *,
    plugin: Optional[str]=None, 
    extension: Optional[str]=None, 
    **kwargs,
) -> Result[Path, str]:
    """Writes an image to a uniform resource identifier (URI)."""
    try:
        iio.imwrite(
            uri, 
            image, 
            plugin=None, 
            extension=None, 
            format_hint=None, 
            **kwargs
        )
        return Ok(uri)
    except IOError as error:
        return Err(str(error))


def read_image(
    uri: str | Path, 
    *, 
    index: Optional[int]=None,
    plugin: Optional[str]=None,
    extension: Optional[str]=None,
    **kwargs,
) -> Result[np.ndarray, str]:
    """Reads an image from a uniform resource identifier (URI)."""
    try:
        image: np.ndarray = iio.imread(
            uri, 
            index=index, 
            plugin=plugin, 
            extension=extension, 
            **kwargs
        )
        return Ok(image)
    except IOError as error:
        return Err(str(error))
