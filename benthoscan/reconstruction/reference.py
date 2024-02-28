""" TODO: Write a docstring. """
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from loguru import logger
from result import Ok, Err, Result

from ..core.io import read_csv

@dataclass(frozen=True)
class Reference():
    """ Data class for camera references. """
    # Types
    Key = str
    Index = int
    Field = str | float | int
    
    # Members
    data: Dict[Key, Dict[Index, Field]]

    def __init__(self, data: Dict[Key, Dict[Index, Field]]) -> object:
        """ Constructor. """
        counts = [len(data[column]) for column in data]
        # Validate that all columns have the same number of samples
        assert all([count == counts[0] for count in counts])
        object.__setattr__(self, "data", data)

    def __iter__(self) -> Index:
        """ Returns the sample indices in the reference. """
        for index in self.indices:
            yield index

    def __getitem__(self, index: Index) -> Dict[Key, Field]:
        """ Returns the column values for the given sample. """
        return dict([(column, self.data[column][index]) \
            for column in self.data])

    @property
    def indices(self, ) -> List[Index]:
        """ Returns the reference indices. """
        column = next(iter(self.data))
        return list(self.data[column].keys())

    @property
    def columns(self) -> List[Key]:
        """ Returns the reference columns. """
        return list(self.data.keys())

    @property
    def count(self) -> int:
        """ Returns the number of reference samples. """
        key = next(iter(self.data))
        return len(self.data[key])

    def keys(self) -> List[Key]:
        """ Returns the keys in the reference. """
        return list(self.data.keys())

    def has_key(self, key: Key) -> None:
        """ TODO """
        pass


def read_reference_from_file(filepath: Path) -> Result[Reference, str]:
    """ Reads a reference from file. """
    match filepath.suffix:
        case ".csv":
            result = read_csv(filepath)
            return Ok(Reference(result.unwrap()))
        case _:
            return Err("invalid reference file format")
