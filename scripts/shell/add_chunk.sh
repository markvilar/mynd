#!/usr/bin/bash

DEVICE="/media/martin/pcie_01"

PROJECT_DIR="$DEVICE/metashape_projects"
DATA_DIR="$DEVICE/acfr_revisits_processed"
CONFIG_DIR="$PWD/config"

# poetry run create <document> [--new] <data_directory> <chunks>
poetry run create "$PROJECT_DIR/qd61g27j_script.psz" --new "$DATA_DIR" "$CONFIG_DIR/chunks/qd61g27j.toml"

exit 0
