""" Functionality for images. """

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

GroupKey = str
ItemKey = str

@dataclass
class ImageFileGroup:
    items: Dict[GroupKey, Dict[ItemKey, Path]]
