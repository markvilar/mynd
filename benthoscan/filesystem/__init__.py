""" This module contains functionality for filesystem objects, i.e. files and
directories. """
from .registry import FileRegistry, create_file_registry
from .search import (
    find_files, 
    find_files_with_extension,
    find_files_with_pattern, 
    list_directory
)
