""" 
Module with read and write functionality for configuration files with
support for various formats such as YAML and TOML. 
"""

import json

from pathlib import Path
from typing import Dict, TypeAlias

import toml
import yaml

from result import Ok, Err, Result


WriteResult: TypeAlias = Result[Path, str]


def write_json(data: Dict, path: Path, mode: str = "w") -> WriteResult:
    """Writes data to a JSON file."""
    try:
        with open(path, mode) as filehandle:
            json.dump(data, filehandle, indent=4)
            return Ok(path)
    except BaseException as error:
        return Err(f"error when writing to file: {str(error)}")


def write_toml(data: Dict, path: Path, mode: str = "w") -> WriteResult:
    """Writes data to a TOML file."""
    try:
        with open(path, mode) as filehandle:
            toml.dump(data, filehandle)
            return Ok(path)
    except BaseException as error:
        return Err(f"error when writing to file: {str(error)}")


def write_yaml(data: Dict, path: Path, mode: str = "w") -> WriteResult:
    """Writes data to a YAML file."""
    try:
        with open(path, mode) as filehandle:
            yaml.dump(data, filehandle, default_flow_style=False)
            return Ok(path)
    except BaseException as error:
        return Err(f"error when writing to file: {str(error)}")


def write_dict_to_file(data: Dict, path: Path, mode: str = "w") -> WriteResult:
    """Writes a dictionary to file. Supported formats are TOML and YAML."""
    match path.suffix:
        case ".json":
            return write_json(data, path, mode)
        case ".toml":
            return write_toml(data, path, mode)
        case ".yml" | ".yaml":
            return write_yaml(data, path, mode)
        case other:
            return Err(f"invalid configuration file format: {path.suffix}")
