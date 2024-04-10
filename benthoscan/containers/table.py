""" Module for data table class. """

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, TypeAlias, Optional

from loguru import logger
from result import Ok, Err, Result

from benthoscan.io import read_csv


@dataclass(frozen=True)
class DataTable:
    """Data class for camera references."""

    Column: TypeAlias = str
    Row: TypeAlias = int
    Value: TypeAlias = str | float | int

    # Members
    data: Dict[Column, Dict[Row, Value]] = field(default_factory=dict)

    def __init__(self, data: Dict[Column, Dict[Row, Value]]) -> object:
        """Constructor."""
        counts = [len(data[column]) for column in data]
        # Validate that all columns have the same number of samples
        assert all([count == counts[0] for count in counts])
        object.__setattr__(self, "data", data)

    def __iter__(self) -> Row:
        """Returns the sample indices in the reference."""
        for index in self.indices:
            yield index

    def __getitem__(self, row: Row) -> Dict[Column, Value]:
        """Returns the column values for a given row."""
        return dict([(column, self.data[column][row]) for column in self.data])

    def __len__(self) -> int:
        """Returns the number of samples."""
        return len(self.indices)

    def __contains__(self, column: Column):
        return column in self.data

    @property
    def indices(self) -> List[Row]:
        """Returns the table row indices."""
        column = next(iter(self.data))
        return list(self.data[column].keys())

    @property
    def columns(self) -> List[Column]:
        """Returns the table columns."""
        return list(self.data.keys())

    @property
    def count(self) -> int:
        """Returns the number of rows."""
        field = next(iter(self.data))
        return len(self.data[field])

    def has_column(self, column: Column) -> bool:
        """Returns true if the column is in the table."""
        return column in self.data

    def get_column(self, column: Column) -> Dict[Row, Value]:
        """Returns the row values for the column."""
        if not self.has_column(column):
            return dict()
        return self.data[column]

    def items(self) -> Dict[Row, Dict[Column, Value]]:
        """Returns the items with the corresponding field values in the
        reference."""
        items = dict()
        for index in self.indices:
            items[index] = self[index]
        return items


@dataclass
class TableFieldMap:
    """Data class representing a map from table column to a field with the
    possibility of requiring existance and adding default value."""

    Value = str | int | float

    name: str
    column: str
    required: bool = False
    default: Optional[Value] = None


def read_table(filepath: Path) -> Result[DataTable, str]:
    """Reads a table of data from file."""
    match filepath.suffix:
        case ".csv":
            result = read_csv(filepath)
            return Ok(DataTable(result.unwrap()))
        case _:
            return Err("invalid reference file format")
