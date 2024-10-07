"""Module for creating image bundles and loaders."""

import functools

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ...image import Image, ImageBundle, ImageBundleLoader
from ...io import read_image


def generate_image_bundle_loaders(
    colors: Iterable[Path], ranges: Iterable[Path], normals: Iterable[Path]
) -> dict[str, ImageBundleLoader]:
    """Generates image bundle loaders by matching image files from directories."""

    file_bundles: dict[str, ImageFileBundle] = _match_image_files_by_label(
        colors=colors,
        ranges=ranges,
        normals=normals,
    )

    file_bundles: dict[str, ImageFileBundle] = _validate_image_file_bundles(
        file_bundles
    )

    return {
        label: functools.partial(_load_image_bundle, files=files)
        for label, files in file_bundles.items()
    }


@dataclass
class ImageFileBundle:
    """Class representing a bundle of image files."""

    colors: Path
    ranges: Path
    normals: Path


def _load_image_bundle(files: ImageFileBundle) -> ImageBundle:
    """Loads an image bundle from files."""

    colors: Image = read_image(files.colors).unwrap()
    ranges: Image = read_image(files.ranges).unwrap()
    normals: Image = read_image(files.normals).unwrap()

    return ImageBundle(colors, ranges, normals)


def _match_image_files_by_label(
    colors: list[Path], ranges: list[Path], normals: list[Path]
) -> list[ImageFileBundle]:
    """Generates frame files by matching files based on stems."""

    color_lookup: dict[str, Path] = {path.stem: path for path in colors}
    range_lookup: dict[str, Path] = {path.stem: path for path in ranges}
    normal_lookup: dict[str, Path] = {path.stem: path for path in normals}

    frame_files: dict[str, ImageFileBundle] = dict()
    for label in color_lookup:
        if label not in range_lookup:
            continue
        if label not in normal_lookup:
            continue

        frame_files[label] = ImageFileBundle(
            colors=color_lookup.get(label),
            ranges=range_lookup.get(label),
            normals=normal_lookup.get(label),
        )

    return frame_files


def _validate_image_file_bundles(
    file_bundles: dict[str, ImageFileBundle],
) -> dict[str, ImageFileBundle]:
    """Validates the image file bundles and removes invalid bundles. Returns
    valid file bundles."""

    for label, files in file_bundles.items():
        if not files.colors or not files.ranges or not files.normals:
            file_bundles.pop(label)

    return file_bundles
