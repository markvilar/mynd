""" 
Module with read and write functionality for configuration files with
support for various formats such as YAML and TOML. 
"""

import json

from pathlib import Path
from typing import Dict, TypeAlias

import toml
import yaml

from result import Ok, Err, Result, is_ok, is_err


ReadResult: TypeAlias = Result[Dict, str]


def read_dict_from_json(path: Path, mode: str = "r") -> ReadResult:
    """Reads a dictionary from JSON file."""
    try:
        with open(path, mode) as filehandle:
            return Ok(json.load(filehandle))
    except BaseException as error:
        return Err(f"error when reading config: {str(error)}")


def read_dict_from_toml(path: Path, mode: str = "r") -> ReadResult:
    """Reads a dictionary from a TOML file."""
    try:
        with open(path, mode) as filehandle:
            return Ok(toml.load(filehandle))
    except BaseException as error:
        return Err(f"error when reading config: {str(error)}")


def read_dict_from_yaml(path: Path, mode: str = "r") -> ReadResult:
    """Reads data from a YAML file."""
    try:
        with open(path, mode) as filehandle:
            return Ok(yaml.safe_load(filehandle))
    except BaseException as error:
        return Err(f"error when reading config: {str(error)}")


def read_dict_from_file(path: Path, mode: str = "r") -> ReadResult:
    """Reads a dictionary from file. Supported formats are JSON, TOML, and YAML."""
    match path.suffix:
        case ".json":
            return read_dict_from_json(path, mode)
        case ".toml":
            return read_dict_from_toml(path, mode)
        case ".yml" | ".yaml":
            return read_dict_from_yaml(path, mode)
        case other:
            return Err(f"invalid configuration file format: {path.suffix}")
