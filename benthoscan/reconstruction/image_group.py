""" TODO: Create docstring """
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from loguru import logger

from .reference import Reference

@dataclass
class Table():
    """ Data class for groups of files. """
    Key = str
    Index = int
    groups: OrderedDict[Key, Dict[Index, Path]]

def create_target_images_from_reference(
    references: Reference,
    group_keys: List[str],
) -> Table:
    """ Returns list of target groups. """
    # Get master files
    groups = OrderedDict()
    for key in group_keys:
        column = dict()
        for index in references:
            filename = Path(references[index][key])
            column[index] = filename
        groups[key] = column
        
    return Table(groups)
