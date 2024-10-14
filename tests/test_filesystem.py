"""Unit tests for mynds filesystem functionality."""

from pathlib import Path

import pytest
from unittest.mock import patch

from mynd.utils.filesystem import (
    list_directory,
    search_files,
    create_resource,
    label_resource_by_stem,
    Resource,
    ResourceManager,
)


# Tests for list_directory
def test_list_directory():
    with patch('glob.glob') as mock_glob:
        mock_glob.return_value = ['/path/file1.txt', '/path/file2.txt']
        result = list_directory(Path('/path'), '*.txt')
        assert len(result) == 2
        assert all(isinstance(item, Path) for item in result)
        mock_glob.assert_called_once_with('/path/*.txt')


# Tests for search_files
def test_search_files():
    with patch('glob.glob') as mock_glob:
        mock_glob.return_value = ['/path/file1.txt', '/path/file2.txt']
        result = search_files('*.txt')
        assert len(result) == 2
        assert all(isinstance(item, Path) for item in result)
        mock_glob.assert_called_once_with('*.txt')


# Tests for Resource class
def test_resource_file():
    file_path = Path('/path/file.txt')
    with patch.object(Path, 'is_file', return_value=True):
        with patch.object(Path, 'is_dir', return_value=False):
            resource = Resource(file_path)
            assert resource.handle == file_path
            assert resource.is_file()
            assert not resource.is_directory()


def test_resource_directory():
    dir_path = Path('/path/dir')
    with patch.object(Path, 'is_file', return_value=False):
        with patch.object(Path, 'is_dir', return_value=True):
            resource = Resource(dir_path)
            assert resource.handle == dir_path
            assert not resource.is_file()
            assert resource.is_directory()


# Tests for create_resource
def test_create_resource_existing():
    with patch.object(Path, 'exists', return_value=True):
        resource = create_resource(Path('/path/file.txt'))
        assert isinstance(resource, Resource)


def test_create_resource_non_existing():
    with patch.object(Path, 'exists', return_value=False):
        resource = create_resource(Path('/path/nonexistent.txt'))
        assert resource is None


# Tests for label_resource_by_stem
def test_label_resource_by_stem_file():
    file_path = Path('/path/file.txt')
    with patch.object(Path, 'is_file', return_value=True):
        with patch.object(Path, 'is_dir', return_value=False):
            resource = Resource(file_path)
            assert label_resource_by_stem(resource) == 'file'


def test_label_resource_by_stem_directory():
    dir_path = Path('/path/dir')
    with patch.object(Path, 'is_file', return_value=False):
        with patch.object(Path, 'is_dir', return_value=True):
            resource = Resource(dir_path)
            assert label_resource_by_stem(resource) == 'dir'


def test_label_resource_by_stem_invalid():
    invalid_path = Path('/path/invalid')
    with patch.object(Path, 'is_file', return_value=False):
        with patch.object(Path, 'is_dir', return_value=False):
            resource = Resource(invalid_path)
            with pytest.raises(NotImplementedError):
                label_resource_by_stem(resource)


# Tests for ResourceManager class
@pytest.fixture
def resource_manager():
    return ResourceManager()


def test_add_resource(resource_manager):
    file_path = Path('/path/file.txt')
    with patch.object(Path, 'is_file', return_value=True):
        with patch.object(Path, 'is_dir', return_value=False):
            resource = Resource(file_path)
            resource_manager.add_resource(resource, ['tag1', 'tag2'])
            identifiers = resource_manager.get_identifiers()
            assert len(identifiers) == 1
            assert identifiers[0].label == 'file'


def test_add_resources(resource_manager):
    file_paths = [Path('/path/file1.txt'), Path('/path/file2.txt')]
    with patch.object(Path, 'is_file', return_value=True):
        with patch.object(Path, 'is_dir', return_value=False):
            resources = [Resource(path) for path in file_paths]
            resource_manager.add_resources(resources, ['tag1'])
            identifiers = resource_manager.get_identifiers()
            assert len(identifiers) == 2


def test_query_tags(resource_manager):
    file_paths = [Path('/path/file1.txt'), Path('/path/file2.txt')]
    with patch.object(Path, 'is_file', return_value=True):
        with patch.object(Path, 'is_dir', return_value=False):
            resource1 = Resource(file_paths[0])
            resource2 = Resource(file_paths[1])
            resource_manager.add_resource(resource1, ['tag1', 'tag2'])
            resource_manager.add_resource(resource2, ['tag2', 'tag3'])

            result = resource_manager.query_tags(['tag2'])
            assert len(result) == 2

            result = resource_manager.query_tags(['tag1', 'tag2'])
            assert len(result) == 1
            assert result[0].handle == file_paths[0]
