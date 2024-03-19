"""This module contains functionality for configuring a chunk with images,
references, and camera calibrations."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, TypeAlias

from loguru import logger
from result import Ok, Err, Result

from benthoscan.containers import FileRegistry
from benthoscan.datatypes import CameraAssemblyFactory
from benthoscan.project import Chunk


def configure_chunk(
    chunk: Chunk,
    assembly_factory: CameraAssemblyFactory,
    registry: FileRegistry,
) -> None:
    """Configures a chunk with reference images."""

    assemblies: List[CameraAssembly] = assembly_factory()

    # TODO: Check that image files are in registry

    # TODO: Add camera assemblies to chunk

    # TODO: Add references

    # TODO: Configure camera calibration
