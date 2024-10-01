"""Module for the database ingest facade."""

from collections.abc import Iterable
from typing import Optional

import tqdm

from ...camera import Camera
from ...image import ImageBundle, ImageBundleLoader
from ...utils.generators import generate_chunked_items
from ...utils.result import Ok, Err, Result

from .database import H5Database

from .details.allocators import (
    ImageBundleBuffers,
    ImageBundleStorage,
    allocate_bundle_buffers,
    allocate_bundle_storage,
)

from .details.bundle_templates import (
    ImageBundleTemplate,
    ImageBundleValidator,
    create_image_bundle_template,
    create_image_bundle_validator,
)


CameraID = Camera.Identifier


def insert_image_bundles_into(
    group: H5Database.Group,
    bundle_loaders: Iterable[ImageBundleLoader],
    *,
    chunk_size: int = 100,
) -> Result[None, str]:
    """Inserts a collection of image bundles into a database group. Assumes that
    the images are captured by the same sensor and that each component of the image
    bundles have the same width, height, and data type.

    Arguments:
        group:              root storage group for the image bundles
        bundle_loaders:     loaders for the bundled images
        chunk_size:         number of bundles storage in chunk
    """

    bundle_count: int = len(bundle_loaders)

    if bundle_count == 0:
        return Err("no bundle loaders provided for insertion")

    template: ImageBundleTemplate = create_image_bundle_template(
        bundle_loaders[0]()
    )
    validator: ImageBundleValidator = create_image_bundle_validator(template)
    storage: ImageBundleStorage = allocate_bundle_storage(
        group, template, bundle_count
    )

    buffer_offset: int = 0
    loader_chunks: list[ImageBundleLoader] = generate_chunked_items(
        bundle_loaders, chunk_size
    )

    for loaders in tqdm.tqdm(loader_chunks, desc="Loading bundles..."):

        buffer_size: int = len(loaders)

        buffers: ImageBundleBuffers = allocate_bundle_buffers(
            template, buffer_size
        )

        load_buffer_result: Result[ImageBundleBuffers, str] = (
            _load_bundles_into(
                buffers=buffers,
                loaders=loaders,
                validator=validator,
            )
        )

        match load_buffer_result:
            case Ok(buffers):
                buffers: ImageBundleBuffers = load_buffer_result.ok()
                _load_buffers_into(storage, buffers, buffer_offset)
                buffer_offset += buffer_size
            case Err(message):
                return Err(message)

    return Ok(None)


def _load_buffers_into(
    storage: ImageBundleStorage,
    buffers: ImageBundleBuffers,
    offset: int,
) -> None:
    """Loads image bundle buffers into storage."""

    count: int = buffers.bundle_count()

    storage.intensities[offset : offset + count] = buffers.intensities
    storage.ranges[offset : offset + count] = buffers.ranges
    storage.normals[offset : offset + count] = buffers.normals


def _load_bundles_into(
    buffers: ImageBundleBuffers,
    loaders: Iterable[ImageBundleLoader],
    validator: Optional[ImageBundleValidator] = None,
) -> Result[ImageBundleBuffers, str]:
    """Loads a collection of image bundles into buffers. If a validator is provided,
    a validation check is performed for each loaded bundle."""

    for index, loader in enumerate(loaders):
        bundle: ImageBundle = loader()

        if validator:
            is_valid: bool = validator(bundle)
            if not is_valid:
                return Err(f"image bundle {index} does not fit template")

        buffers.intensities[index] = bundle.intensities.data
        buffers.ranges[index] = bundle.ranges.data
        buffers.normals[index] = bundle.normals.data

    return Ok(buffers)
