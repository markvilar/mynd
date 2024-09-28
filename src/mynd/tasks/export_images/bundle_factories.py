"""Module for creating image bundles and loaders."""

import functools
import glob

from dataclasses import dataclass
from pathlib import Path

from ...camera import Image, ImageBundle, ImageBundleLoader
from ...io import read_image


def generate_image_bundle_loaders(
    image_directory: Path,
    range_directory: Path,
    normal_directory: Path,
    pattern: str,
) -> dict[str, ImageBundleLoader]:
    """Generates loaders from a collection of image bundles."""

    file_bundles: list[_ImageFileBundle] = _bundle_image_files(
        image_directory,
        range_directory,
        normal_directory,
        pattern,
    )

    file_bundles: list[_ImageFileBundle] = _validate_image_file_bundles(file_bundles)

    file_bundles: list[_ImageFileBundle] = sorted(
        file_bundles, key=lambda item: item.label, reverse=True
    )

    return {files.label: functools.partial(_load_image_bundle, files=files) for files in file_bundles}


@dataclass
class _ImageFileBundle:
    """Class representing a bundle of image files."""

    label: str
    intensities: Path
    ranges: Path
    normals: Path


def _load_image_bundle(files: _ImageFileBundle) -> ImageBundle:
    """Loads an image bundle from files."""

    label: str = files.label
    intensities: Image = read_image(files.intensities).unwrap()
    ranges: Image = read_image(files.ranges).unwrap()
    normals: Image = read_image(files.normals).unwrap()

    return ImageBundle(label, intensities, ranges, normals)


def _match_image_files_by_label(
    image_files: list[Path], range_files: list[Path], normal_files: list[Path]
) -> list[_ImageFileBundle]:
    """Generates frame files by matching files based on stems."""

    image_lookup: dict[str, Path] = {path.stem: path for path in image_files}
    range_lookup: dict[str, Path] = {path.stem: path for path in range_files}
    normal_lookup: dict[str, Path] = {path.stem: path for path in normal_files}

    frame_files: list[_ImageFileBundle] = list()
    for label in image_lookup:
        if label not in range_lookup:
            continue
        if label not in normal_lookup:
            continue

        frame_files.append(
            _ImageFileBundle(
                label=label,
                intensities=image_lookup.get(label),
                ranges=range_lookup.get(label),
                normals=normal_lookup.get(label),
            )
        )

    return frame_files


def _validate_image_file_bundles(
    file_bundles: list[_ImageFileBundle],
) -> list[_ImageFileBundle]:
    """Validates the image file bundles and removes invalid bundles. Returns
    valid file bundles."""

    for files in file_bundles:
        if not files.intensities or not files.ranges or not files.normals:
            file_bundles.remove(files)

    return file_bundles


def _bundle_image_files(
    image_directory: Path,
    range_directory: Path,
    normal_directory: Path,
    pattern: str,
) -> list[_ImageFileBundle]:
    """List directory files and generate frame files by matching file stems."""

    file_bundles: list[_ImageFileBundle] = list()

    image_files: list[Path] = [
        Path(path) for path in glob.glob(str(image_directory / pattern))
    ]
    range_files: list[Path] = [
        Path(path) for path in glob.glob(str(range_directory / pattern))
    ]
    normal_files: list[Path] = [
        Path(path) for path in glob.glob(str(normal_directory / pattern))
    ]

    file_bundles: list[_ImageFileBundle] = _match_image_files_by_label(
        image_files=image_files,
        range_files=range_files,
        normal_files=normal_files,
    )

    return file_bundles
