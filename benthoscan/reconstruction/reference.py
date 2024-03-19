""" TODO: Write a docstring. """
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, TypeAlias

from loguru import logger
from result import Ok, Err, Result

from benthoscan.io import read_csv

@dataclass(frozen=True)
class Reference():
    """ Data class for camera references. """
    Field: TypeAlias = str
    Entity: TypeAlias = int
    Value: TypeAlias = str | float | int
    
    # Members
    data: Dict[Field, Dict[Entity, Value]] = field(default_factory=dict)

    def __init__(self, data: Dict[Field, Dict[Entity, Value]]) -> object:
        """ Constructor. """
        counts = [len(data[column]) for column in data]
        # Validate that all columns have the same number of samples
        assert all([count == counts[0] for count in counts])
        object.__setattr__(self, "data", data)

    def __iter__(self) -> Entity:
        """ Returns the sample indices in the reference. """
        for index in self.indices:
            yield index

    def __getitem__(self, index: Entity) -> Dict[Field, Value]:
        """ Returns the column values for the given sample. """
        return dict([(column, self.data[column][index]) \
            for column in self.data])

    def __len__(self) -> int:
        """ Returns the number of samples. """
        return len(self.indices)

    def __contains__(self, field: Field):
        return field in self.data

    @property
    def entities(self) -> List[Entity]:
        """ Returns the reference indices. """
        field = next(iter(self.data))
        return list(self.data[field].keys())

    @property
    def fields(self) -> List[Field]:
        """ Returns the reference columns. """
        return list(self.data.keys())

    @property
    def count(self) -> int:
        """ Returns the number of entities. """
        field = next(iter(self.data))
        return len(self.data[field])

    def fields(self) -> List[Field]:
        """ Returns the fields in the reference. """
        return list(self.data.keys())

    def has_field(self, field: Field) -> bool:
        """ Returns true if the reference contains the field. """
        return field in self.data

    def get_values(self, field: Field) -> Dict[Entity, Value]:
        """ Returns the item and values. """
        if not self.has_field(field):
            return dict()
        return self.data[field]


def read_reference_from_file(filepath: Path) -> Result[Reference, str]:
    """ Reads a reference from file. """
    match filepath.suffix:
        case ".csv":
            result = read_csv(filepath)
            return Ok(Reference(result.unwrap()))
        case _:
            return Err("invalid reference file format")
