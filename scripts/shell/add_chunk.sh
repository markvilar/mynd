#!/usr/bin/bash

PROJECT_DIR="$HOME/data/metashape_projects"
DATA_DIR="/media/martin/pcie_01/acfr_revisits_processed"
CONFIG_DIR="$PWD/config"

# poetry run create <document> [--new] <data_directory> <chunks>
poetry run create "$PROJECT_DIR/r23685bc_script.psz" --new "$DATA_DIR" "$CONFIG_DIR/dev/r23685bc.toml"

exit 0
