""" TODO: Create docstring """
from collections import OrderedDict
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Dict, Callable, List

from loguru import logger

from benthoscan.filesystem import (
    find_files_with_extension,
    find_files_with_pattern
)

from .reference import Reference

FileLabel = str
FileLabelGroup = Dict[str, FileLabel]
FileGroup = Dict[str, Path]

# TODO: Replace with file registry
LabelledFiles = Dict[FileLabel, Path]

def create_file_labels_from_references(
    references: Reference,
    target_keys: List[str],
) -> List[FileLabelGroup]:
    """ Returns list of target groups. """
    file_groups = list()
    for index in references:
        files = dict()
        for key in target_keys:
            files[key] = references[index][key]
        file_groups.append(files)
    return file_groups

FileRetriever = Callable[[FileLabelGroup, LabelledFiles], List[FileGroup]]

def retrieve_files_by_label(
    labels: Dict[str, str],
    labelled_files: Dict[str, Path],
) -> Dict[str, Path]:
    """ Matches files in the file groups with the reference files. """
    # Match file groups to reference files
    retrieved_files: Dict[str, Path] = dict()
    for group in labels:
        label = labels[group]
        if not label in labelled_files:
            logger.warning(f"Missing label: {label}")
            break
        retrieved_files[group] = labelled_files[label]
    if not retrieved_files.keys() == labels.keys():
        return None
    return retrieved_files

def retrieve_files(
    label_groups: List[FileLabelGroup],
    retrieve_fun: FileRetriever,
) -> List[FileGroup]:
    """ Matches the file group paths to the provided file paths. Returns the
    matched filegroups. """
    retrieved_files = list()
    for label_group in label_groups:
        retrieved = retrieve_fun(label_group)
        if retrieved:
            retrieved_files.append(retrieved)
    return retrieved_files

def create_file_groups(
    directory: Path, # TODO: Replace with file registry
    references: Reference, 
    reference_keys: List[str],
) -> List[FileGroup]:
    """ TODO: """

    # TODO: Implement query strategy
    # TODO: Implement group strategy
    # TODO: Implement match strategy
    
    # Query strategy - search directory for files
    image_files = find_files_with_extension(
        directory,
        extensions = [".jpeg", ".jpg", ".png", ".tif", ".tiff"],
    )

    logger.info(f"Found {len(image_files)} image files.")

    # Group strategy - create groups from reference
    file_labels: List[FileLabelGroup] = create_file_labels_from_references(
        references,
        reference_keys,
    )

    # TODO: Move to file registry
    # Create path lookup table with filename as labels
    image_lookup: Dict[str, Path] = dict([
        (path.name, path) for path in image_files
    ])

    retriever = partial(
        retrieve_files_by_label,
        labelled_files = image_lookup,
    )

    retrieved_file_groups = retrieve_files(file_labels, retriever) 
    return retrieved_file_groups
