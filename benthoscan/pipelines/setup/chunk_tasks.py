""" Functions for """

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple, TypeAlias

import Metashape

from loguru import logger
from result import Ok, Err, Result

from benthoscan.project import Chunk

GroupKey: TypeAlias = str
Index: TypeAlias = int


def convert_file_collections_to_compositions(
    file_collections: Dict[GroupKey, Dict[Index, Path]],
) -> Dict[Index, Dict[GroupKey, Path]]:
    """Converts groups of files to compositions with file group components."""
    file_compositions = dict()
    for group in file_collections:
        files = file_collections[group]
        for index in files:
            if not index in file_compositions:
                file_compositions[index] = dict()
            file_compositions[index][group] = files[index]
    return file_compositions


def check_equal_component_count(
    file_compositions: Dict[Index, Dict[GroupKey, Path]]
) -> bool:
    """Checks if all compositions have the same number of components."""
    # Validate groups (number of groups, and group keys)
    counts = [len(file_compositions[index]) for index in file_compositions]
    return all([count == counts[0] for count in counts])


def check_equal_component_keys(
    file_compositions: Dict[Index, Dict[GroupKey, Path]]
) -> bool:
    """Checks if all compositions have the same keys. The keys of the first
    composition is used as template for the checks."""
    first_key = next(iter(file_compositions))
    first_item = file_compositions[first_key]
    template_keys = set(first_item.keys())
    checks = dict()
    for index, components in file_compositions.items():
        component_keys = set(components.keys())
        checks[index] = component_keys == template_keys
    return all([checks[index] for index in checks])


def get_composition_files_and_count(
    compositions: Dict[Index, Dict[GroupKey, Path]], ordering: List[GroupKey]
) -> Tuple[List[Path], List[int]]:
    """Returns the file names and counts for a list of compositions."""
    filenames, filecounts = list(), list()
    for index in compositions:
        composition = compositions[index]
        for key in ordering:
            filenames.append(str(composition[key]))
        filecounts.append(len(ordering))
    return filenames, filecounts


def add_composed_images_to_chunk(
    chunk: Chunk,
    file_collections: Dict[GroupKey, Dict[Index, Path]],
    group_order: List[GroupKey],
    progress_fun: Callable[[float], None] = lambda percent: None,
) -> Result[int, str]:
    """
    Adds groups of images to a chunk. The images are formatted in item-based
    order, meaning that each item has images from several sources.
    The function assumes that all items have the same set of sources.

    Example collections:
        "left" : { 0: "left_00.png", 1 : "left_01.png" }
        "right" : { 0: "right_00.png", 1 : "right_01.png" }

    Compositions of the example collections:
        0: { "left" : "left_00.png", "right" : "right_00.png" }
        1: { "left" : "left_01.png", "right" : "right_01.png" }
    """
    # Create compositions from collections
    file_compositions = convert_file_collections_to_compositions(file_collections)

    # Validate compositions
    check_status = {
        "equal_counts": check_equal_component_count(file_compositions),
        "equal_keys": check_equal_component_keys(file_compositions),
    }

    for key, success in check_status.items():
        if not success:
            return Err(f"Check failed: {key}")

    # Create file names and groups for each composition
    filenames, filegroups = get_composition_files_and_count(
        file_compositions,
        group_order,
    )

    # Validate that the number of filenames and group elements are equal
    if len(filenames) != sum(filegroups):
        return Err(f"unequal number of files and group elements")

    # Add images to chunk
    try:
        chunk.addPhotos(
            filenames=filenames,
            filegroups=filegroups,
            layout=Metashape.MultiplaneLayout,
            progress=progress_fun,
        )
    except RuntimeError as error:
        return Err(str(error))

    return Ok(len(filegroups))


def add_camera_references(
    chunk: Chunk,
    camera_references,
) -> Result[bool, str]:
    """Add reference from memory."""

    logger.info(f"Reference: {reference.fields}")
    logger.info(f"Config:    {config}")

    input("Press a key...")

    # TODO: Get reference keys
    labels = list(reference.get_field(config.label_field).values())
    labels = list(reference.get_field(config.label_field).values())

    # labels = list(reference.get_field("stereo_left_label").values())

    reference_data = reference.items()

    for item in reference_data:
        logger.info(f"Index: {item}")

    input("Press a key...")

    # Camera lookup
    camera_lookup = dict([(camera.label, camera) for camera in chunk.cameras])

    for label in labels:
        logger.info(f"Label:  {label}")

    for camera in chunk.cameras:
        logger.info(f"Camera: {camera.label}")
        if camera.label in labels:
            logger.info("Left")
        else:
            logger.info("Unknown")

    return Ok(True)
