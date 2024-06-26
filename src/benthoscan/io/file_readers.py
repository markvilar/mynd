"""Module for reading data from files. Supported formats are CSV, JSON, YAML and TOML."""

import json

from pathlib import Path

import polars as pl
import toml
import yaml

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
    if not path.suffix == ".json":
        return Err(f"invalid json file: {path}")

    try:
        with open(path, mode) as filehandle:
            return Ok(json.load(filehandle))
    except BaseException as error:
        return Err(f"error when reading config: {str(error)}")


def read_toml(path: Path, mode: str = "r") -> Result[dict, str]:
    """Reads data from a TOML file."""
    if not path.suffix == ".toml":
        return Err(f"invalid toml file: {path}")

    try:
        with open(path, mode) as filehandle:
            return Ok(toml.load(filehandle))
    except BaseException as error:
        return Err(f"error when reading config: {str(error)}")


def read_yaml(path: Path, mode: str = "r") -> Result[dict, str]:
    """Reads data from a YAML file."""
    if not path.suffix == ".yaml" | ".yml":
        return Err(f"invalid yaml file: {path}")

    try:
        with open(path, mode) as filehandle:
            return Ok(yaml.safe_load(filehandle))
    except BaseException as error:
        return Err(f"error when reading config: {str(error)}")


def read_dict_from_file(path: Path, mode: str = "r") -> Result[dict, str]:
    """Reads a dictionary from file. Supported formats are JSON, TOML, and YAML."""
    match path.suffix:
        case ".json":
            return read_json(path, mode)
        case ".toml":
            return read_toml(path, mode)
        case ".yml" | ".yaml":
            return read_yaml(path, mode)
        case other:
            return Err(f"invalid configuration file format: {path.suffix}")
