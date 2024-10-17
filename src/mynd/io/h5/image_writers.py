"""Module for the database ingest facade."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import tqdm

from mynd.image import (
    Image,
    ImageLayout,
    PixelFormat,
    ImageType,
    ImageComposite,
    ImageCompositeLoader,
)
from mynd.utils.generators import generate_chunked_items
from mynd.utils.result import Ok, Err, Result

from .database import H5Database

BufferMap = Mapping[ImageType, np.ndarray]
DatasetMap = Mapping[ImageType, H5Database.Dataset]
ImageCompositeValidator = Callable[[ImageComposite], bool]


def insert_image_composites_into(
    group: H5Database.Group,
    composite_loaders: Iterable[ImageCompositeLoader],
    *,
    chunk_size: int = 100,
) -> Result[None, str]:
    """Inserts a collection of image composites into a database group. Assumes that
    the images are captured by the same sensor and that each component of the image
    composites have the same width, height, and data type.

    :arg group:                 root storage group for the image composites
    :arg composite_loaders:     loaders for the composited images
    :arg chunk_size:            number of composites storage in chunk
    """

    composite_count: int = len(composite_loaders)

    if composite_count == 0:
        return Err("no composite loaders provided for insertion")

    template: ImageCompositeTemplate = create_image_composite_template(
        composite_loaders[0]()
    )

    validator: ImageCompositeValidator = create_image_composite_validator(
        template
    )

    datasets: DatasetMap = allocate_image_composite_storage(
        group, template, composite_count
    )

    buffer_offset: int = 0
    loader_chunks: list[ImageCompositeLoader] = generate_chunked_items(
        composite_loaders, chunk_size
    )

    for loaders in tqdm.tqdm(loader_chunks, desc="Loading composites..."):

        buffer_size: int = len(loaders)

        buffers: BufferMap = allocate_composite_buffers(template, buffer_size)

        load_buffer_result: Result[BufferMap, str] = _load_composites_into(
            buffers=buffers,
            loaders=loaders,
            validator=validator,
        )

        match load_buffer_result:
            case Ok(buffers):
                buffers: BufferMap = load_buffer_result.ok()
                _load_buffers_into(datasets, buffers, buffer_offset).unwrap()
                buffer_offset += buffer_size
            case Err(message):
                return Err(message)

    return Ok(None)


def _load_buffers_into(
    datasets: DatasetMap,
    buffers: BufferMap,
    offset: int,
) -> Result[None, str]:
    """Loads image composite buffers into storage."""

    for key, buffer in buffers.items():
        if key not in datasets:
            return Err(f"missing dataset for type: {key}")

        size: int = len(buffer)

        dataset: H5Database.Dataset = datasets.get(key)
        dataset[offset : offset + size] = buffer

    return Ok(None)


def _load_composites_into(
    buffers: BufferMap,
    loaders: Iterable[ImageCompositeLoader],
    validator: Optional[ImageCompositeValidator] = None,
) -> Result[BufferMap, str]:
    """Loads a collection of image composites into buffers. If a validator is
    provided, a validation check is performed for each loaded composite."""

    for index, loader in enumerate(loaders):
        composite: ImageComposite = loader()

        if validator:
            is_valid: bool = validator(composite)
            if not is_valid:
                return Err(f"image composite {index} does not fit template")

        for key, image in composite.components.items():
            buffer: Optional[np.ndarray] = buffers.get(key)

            if buffer is None:
                return Err(f"invalid buffer for type: {key}")

            buffer[index] = image.to_array()

    return Ok(buffers)


@dataclass
class ImageTemplate:
    """Class representing an image template with shape, format, and dtype."""

    layout: ImageLayout
    pixel_format: PixelFormat
    dtype: np.dtype


ImageCompositeTemplate = Mapping[ImageType, ImageTemplate]


def create_image_composite_template(
    composite: ImageComposite,
) -> ImageCompositeTemplate:
    """Creates a composite template."""

    template: ImageCompositeTemplate = dict()
    for image_type, image in composite.components.items():
        template[image_type] = ImageTemplate(
            image.layout, image.pixel_format, image.dtype
        )

    return template


def create_image_composite_validator(
    template: ImageCompositeTemplate,
) -> ImageCompositeValidator:
    """Creates an image composite validator based on a composite template."""

    def validate_composite_with_template(composite: ImageComposite) -> bool:
        """Validates an image composite by checking if it fits the image composite template."""
        return _check_image_composite_fits_template(composite, template)

    return validate_composite_with_template


def _check_image_composite_fits_template(
    composite: ImageComposite, template: ImageCompositeTemplate
) -> bool:
    """Returns true if the image composite fits the given template."""

    component_checks: dict[ImageType, bool] = dict()
    for image_type, image in composite.components.items():

        if image_type not in template:
            component_checks[image_type] = False
        else:
            component_checks[image_type] = _check_image_fits_template(
                image, template.get(image_type)
            )

    return all(component_checks.values())


def _check_image_fits_template(image: Image, template: ImageTemplate) -> bool:
    """Returns true if the image fits the given template."""
    return all(
        [
            image.layout == template.layout,
            image.pixel_format == template.pixel_format,
            image.dtype == template.dtype,
        ]
    )


def allocate_composite_buffers(
    template: ImageCompositeTemplate, count: int
) -> BufferMap:
    """Allocates buffers for a given number of image composites."""

    buffers: BufferMap = dict()
    for image_type, component in template.items():
        buffers[image_type] = np.empty(
            shape=(count,) + component.layout.shape,
            dtype=component.dtype,
        )

    return buffers


def allocate_image_composite_storage(
    group: H5Database.Group, template: ImageCompositeTemplate, count: int
) -> DatasetMap:
    """Allocate datasets for the given image composite template and count."""

    datasets: dict[ImageType, H5Database.Dataset] = dict()
    for key, component in template.items():
        datasets[key]: H5Database.Dataset = group.create_dataset(
            str(key),
            shape=(count,) + component.layout.shape,
            dtype=component.dtype,
        )

    return datasets
