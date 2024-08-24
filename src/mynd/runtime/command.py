"""Module for commands to invoke from the command line."""

import sys

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Command:
    """Class representing a command."""

    command: str
    arguments: list[str]


def command_line_arguments() -> Command:
    """Creates a command from command-line arguments."""
    system_arguments: list[str] = sys.argv
    executable, *arguments = system_arguments
    command = Path(executable).stem
    return Command(command, arguments)
