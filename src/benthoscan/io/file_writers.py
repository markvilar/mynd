"""Module for writing data to files. Supported formats are CSV, JSON, YAML,
TOML and msgpack."""

from pathlib import Path

import msgspec
import polars as pl

from result import Ok, Err, Result


def write_csv(data: pl.DataFrame, path: Path, mode: str = "w") -> Result[Path, str]:
    """Writes data to a CSV file."""
    try:
        data.write_csv(path)
        return Ok(path)
    except IOError as error:
        return Err(str(error))


def write_json(data: dict, path: Path, mode: str = "w") -> Result[Path, str]:
    """Writes data to a JSON file."""
    try:
        with open(path, mode) as handle:
            handle.write(msgspec.json.encode(data))
            return Ok(path)
    except IOError as error:
        return Err(str(error))


def write_yaml(data: dict, path: Path, mode: str = "w") -> Result[Path, str]:
    """Writes data to a YAML file."""
    try:
        with open(path, mode) as handle:
            handle.write(msgspec.yaml.encode(data))
            return Ok(path)
    except IOError as error:
        return Err(str(error))


def write_toml(data: dict, path: Path, mode: str = "w") -> Result[Path, str]:
    """Writes data to a TOML file."""
    try:
        with open(path, mode) as handle:
            handle.write(msgspec.toml.encode(data))
            return Ok(path)
    except IOError as error:
        return Err(str(error))


def write_msgpack(data: dict, path: Path, mode: str = "w") -> Result[Path, str]:
    """Writes data to a MSGPACK file."""
    try:
        with open(path, mode) as handle:
            handle.write(msgspec.msgpack.encode(data))
            return Ok(path)
    except IOError as error:
        return Err(str(error))


def write_dict_to_file(data: dict, path: Path, mode: str = "w") -> Result[Path, str]:
    """Writes data to file. Supported formats are JSON, TOML, YAML, and MSGPACK."""
    match path.suffix:
        case ".json":
            return write_json(data, path, mode)
        case ".toml":
            return write_toml(data, path, mode)
        case ".yml" | ".yaml":
            return write_yaml(data, path, mode)
        case ".msgpack":
            return write_msgpack(data, path, mode)
        case other:
            return Err(f"invalid configuration file format: {path.suffix}")
