"""Module for reading data from files. Supported formats are CSV, JSON, YAML,
TOML and msgpack."""

from pathlib import Path

import msgspec
import polars as pl

from result import Ok, Err, Result


def read_csv(path: Path) -> Result[pl.DataFrame, str]:
    """Reads camera references from a CSV file."""
    try:
        dataframe: pl.DataFrame = pl.read_csv(path)
        return Ok(dataframe)
    except BaseException as error:
        return Err(str(error))


def read_json(path: Path, mode: str = "r") -> Result[dict, str]:
    """Reads data from a JSON file."""
    try:
        with open(path, mode=mode) as handle:
            data: dict = msgspec.json.decode(handle.read())
            return Ok(data)
    except IOError as error:
        return Err(str(error))


def read_yaml(path: Path, mode: str = "r") -> Result[dict, str]:
    """Reads data from a YAML file."""
    try:
        with open(path, mode=mode) as handle:
            data: dict = msgspec.yaml.decode(handle.read())
            return Ok(data)
    except IOError as error:
        return Err(str(error))


def read_toml(path: Path, mode: str = "r") -> Result[dict, str]:
    """Reads data from a TOML file."""
    try:
        with open(path, mode=mode) as handle:
            data: dict = msgspec.toml.decode(handle.read())
            return Ok(data)
    except IOError as error:
        return Err(str(error))


def read_msgpack(path: Path, mode: str = "r") -> Result[dict, str]:
    """Reads data from a MSGPACK file."""
    try:
        with open(path, mode=mode) as handle:
            data: dict = msgspec.msgpack.decode(handle.read())
            return Ok(data)
    except IOError as error:
        return Err(str(error))


def read_dict_from_file(path: Path, mode: str = "r") -> Result[dict, str]:
    """Reads data from file. Supported formats are JSON, TOML, YAML, and MSGPACK."""
    match path.suffix:
        case ".json":
            return read_json(path, mode)
        case ".toml":
            return read_toml(path, mode)
        case ".yml" | ".yaml":
            return read_yaml(path, mode)
        case ".msgpack":
            return read_msgpack(path, mode)
        case other:
            return Err(f"invalid configuration file format: {path.suffix}")
