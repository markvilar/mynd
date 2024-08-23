"""Module for reading and writing dataframes to file. Supported format is CSV."""

from pathlib import Path

import polars as pl

from ..utils.result import Ok, Err, Result


def read_data_frame(path: Path) -> Result[pl.DataFrame, str]:
    """Reads a data frame from file."""

    match path.suffix:
        case ".csv":
            return _read_csv(path)
        case _:
            return Err(f"invalid dataframe file format: {path.suffix}")


def _read_csv(path: Path) -> Result[pl.DataFrame, str]:
    """Reads a data frame from a CSV file."""
    try:
        dataframe: pl.DataFrame = pl.read_csv(path)
        return Ok(dataframe)
    except BaseException as error:
        return Err(str(error))


def write_data_frame(
    path: Path, data: pl.DataFrame, mode: str = "w"
) -> Result[Path, str]:
    """Reads a data frame from file."""

    match path.suffix:
        case ".csv":
            return _write_csv(path, data, mode)
        case _:
            return Err(f"invalid dataframe file format: {path.suffix}")


def _write_csv(path: Path, data: pl.DataFrame, mode: str = "w") -> Result[Path, str]:
    """Writes a data frame to a CSV file."""
    try:
        data.write_csv(path)
        return Ok(path)
    except IOError as error:
        return Err(str(error))
