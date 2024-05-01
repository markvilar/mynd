# Benthoscan

![ci](https://github.com/markvilar/benthoscan/actions/workflows/ci.yml/badge.svg)
![pylint](https://github.com/markvilar/benthoscan/actions/workflows/pylint.yml/badge.svg)

Benthoscan is a small API for 3D reconstruction and registration based on images. Benthoscan wraps 
Metashapes Python API for reconstruction and implements a registration module with Open3D.

The repository includes support for the following tools:
* poetry - package management and build tool
* pytest - unit tests
* twine - package release

## Setting up a virtual environment

```shell
# Install pipenv
pip3 install --user poetry
```

### Managing the project environment

```shell
# Specify the desired python version
poetry env use 3.11
```

```shell
poetry env info
```

```shell
poetry env remove
```

### Building and install the project

```shell
poetry build
```

```shell
poetry install
```

### Running tests

```shell
poetry run pytest
```

### Removing dependencies

```shell
poetry remove <package>
```
