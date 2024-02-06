""" 
Module with read and write functionality for configuration files with
support for various formats such as YAML and TOML. 
"""

from pathlib import Path
from typing import Dict

import toml
import yaml

from result import Ok, Err, Result, is_ok, is_err

# -----------------------------------------------------------------------------
# ---- Write functions --------------------------------------------------------
# -----------------------------------------------------------------------------

ConfigReadResult = Result[Dict, str]

def read_toml(path: Path, mode: str="r") -> ConfigReadResult:
    """ Read a toml file. """
    try:
        with open(path, mode) as filehandle:
            contents = toml.load(filehandle)
            return Ok(contents)
    except BaseException as error:
        return Err(f"error when reading config: {str(error)}")

def read_yaml(path: Path, mode: str="r") -> ConfigReadResult:
    """ Read a yaml file. """
    try:
        with open(path, mode) as filehandle:
            contents = yaml.safe_load(filehandle)
            return Ok(contents)
    except BaseException as error:
        return Err(f"error when reading config: {str(error)}")

def read_config(path: Path, mode: str="r") -> ConfigReadResult:
    """ Read a configuration file. Supported formats are TOML and YAML. """
    match path.suffix:
        case ".toml":
            return read_toml(path, mode)
        case ".yml" | ".yaml":
            return read_yaml(path, mode)
        case other:
            return Err(f"invalid configuration file format: {path.suffix}")

# -----------------------------------------------------------------------------
# ---- Write functions --------------------------------------------------------
# -----------------------------------------------------------------------------

ConfigWriteResult = Result[Path, str]

def write_toml(config: Dict, path: Path, mode: str="w") -> ConfigWriteResult:
    """ Writes a dictionary to a TOML file. """
    try:
        with open(path, mode) as filehandle:
            toml.dump(config, filehandle)
            return Ok(path)
    except BaseException as error:
        return Err("error when writing config: {str(error)}")

def write_yaml(config: Dict, path: Path, mode: str="w") -> ConfigWriteResult:
    """ Writes a dictionary to a YAML file. """
    try:
        with open(path, mode) as filehandle:
            yaml.dump(config, filehandle, default_flow_style=False)
            return Ok(path)
    except BaseException as error:
        return Err(f"error when writing config: {str(error)}")

def write_config(config: Dict, path: Path, mode: str="w") -> ConfigWriteResult:
    """ Write a config dictionary to file. Supported formats are TOML and YAML. """
    match path.suffix:
        case ".toml":
            return write_toml(config, path, mode)
        case ".yml" | ".yaml":
            return write_yaml(config, path, mode)
        case other:
            return Err(f"invalid configuration file format: {path.suffix}")
