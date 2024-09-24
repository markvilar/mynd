"""Module for the database ingest facade."""

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypeVar

import tqdm

from ...camera import ImageBundle, ImageBundleLoader
from ...database import H5Database
from ...utils.result import Ok, Err, Result


from .bundle_templates import (
    ImageBundleTemplate,
    create_image_bundle_template,
    check_image_bundle_fits_template,
)

from .storage import (
    ImageBundleBuffers,
    ImageBundleDatasets,
    allocate_bundle_buffers,
    allocate_bundle_datasets,
)


class CreateDatabaseTask:
    """Facade class for create database tasks."""

    @dataclass
    class Config:
        """Class representing a dataset config."""

        output_path: Path
        group_patterns: dict[str, str]


T: TypeVar = TypeVar("T")


def generate_chunks(items: Iterable[T], chunk_size: int) -> Iterable[list[T]]:
    """Generate chunks of the items with the maximum size of chunk size."""
    for index in range(0, len(items), chunk_size):
        yield items[index : index + chunk_size]


def insert_image_bundles_into(
    group: H5Database.Group,
    bundle_loaders: Iterable[ImageBundleLoader],
    chunk_size: int,
) -> Result[None, str]:
    """Inserts a collection of image bundles into a database group."""

    bundle_count: int = len(bundle_loaders)

    if bundle_count == 0:
        return Err("no bundle loaders provided for insertion")

    template: ImageBundleTemplate = create_image_bundle_template(bundle_loaders[0]())
    datasets: ImageBundleDatasets = allocate_bundle_datasets(
        group, template, bundle_count
    )

    running_index: int = 0
    for loaders in tqdm.tqdm(
        generate_chunks(bundle_loaders, chunk_size), desc="Loading bundles..."
    ):

        loader_count: int = len(loaders)

        buffers: ImageBundleBuffers = allocate_bundle_buffers(template, loader_count)

        # TODO: Load image bundles into buffers
        load_buffer_result: Result[ImageBundleBuffers, str] = (
            validate_and_insert_bundles(
                buffers,
                loaders,
                template,
            )
        )

        if load_buffer_result.is_err():
            return load_buffer_result

        buffers: ImageBundleBuffers = load_buffer_result.ok()

        # TODO: Load buffer to dataset
        datasets.labels[running_index : running_index + loader_count] = buffers.labels
        datasets.intensities[running_index : running_index + loader_count] = (
            buffers.intensities
        )
        datasets.ranges[running_index : running_index + loader_count] = buffers.ranges
        datasets.normals[running_index : running_index + loader_count] = buffers.normals

        running_index += loader_count

    return Ok(None)


# TODO: Refactor this function
def validate_and_insert_bundles(
    buffers: ImageBundleBuffers,
    loaders: Iterable[ImageBundleLoader],
    template: Optional[ImageBundleTemplate] = None,
) -> Result[ImageBundleBuffers, str]:
    """Allocates buffers for a collection of image bundles, and performs
    validation by checking that ."""

    for index, loader in enumerate(loaders):
        bundle: ImageBundle = loader()

        if template:
            fits_template: bool = check_image_bundle_fits_template(bundle, template)
            if not fits_template:
                return Err(f"image bundle {bundle.label} does not fit template")

        buffers.labels[index] = bundle.label
        buffers.intensities[index] = bundle.intensities.data
        buffers.ranges[index] = bundle.ranges.data
        buffers.normals[index] = bundle.normals.data

    return Ok(buffers)
