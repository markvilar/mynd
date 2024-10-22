"""Module with common image factories."""

from pathlib import Path
from typing import TypeAlias

from mynd.image import Image, ImageType, ImageComposite, ImageCompositeLoader
from mynd.io import read_image

from mynd.utils.filesystem import list_directory


def build_image_composite_loaders(
    directories: dict[ImageType, Path]
) -> dict[str, ImageCompositeLoader]:
    """Creates a collection of composite image loaders from directories."""

    # List directories
    image_files: dict[ImageType, list[Path]] = {
        image_type: list_directory(directory)
        for image_type, directory in directories.items()
    }

    # Label each file with the stem of the path
    labelled_image_files: dict[ImageType, dict[str, Path]] = {
        image_type: {path.stem: path for path in files}
        for image_type, files in image_files.items()
    }

    ImageFileMap: TypeAlias = dict[ImageType, Path]

    # Match image files with the same label
    matched_image_files: dict[str, ImageFileMap] = dict()
    for image_type, file_map in labelled_image_files.items():
        for label, path in file_map.items():
            if label not in matched_image_files:
                matched_image_files[label] = dict()
            matched_image_files[label][image_type] = path

    # Filter invalid matches
    valid_image_files: dict[str, ImageFileMap] = {
        label: files
        for label, files in matched_image_files.items()
        if ImageType.COLOR in files
        and ImageType.RANGE in files
        and ImageType.NORMAL in files
    }

    # Create loaders
    loaders: dict[str, ImageCompositeLoader] = {
        label: create_image_composite_loader(files)
        for label, files in valid_image_files.items()
    }

    return loaders


def create_image_composite_loader(
    files: dict[ImageType, Path]
) -> ImageCompositeLoader:
    """Create an image composite loader from a collection of components."""

    def load_image_composite() -> ImageComposite:
        """Loads an image composite."""
        components: dict[ImageType, Image] = {
            image_type: read_image(path).unwrap()
            for image_type, path in files.items()
        }
        return ImageComposite(components)

    return load_image_composite
