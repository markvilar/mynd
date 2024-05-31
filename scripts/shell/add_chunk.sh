#!/usr/bin/bash

PROJECT_DIR="$HOME/data/metashape_projects"
DATA_DIR="$HOME/data/acfr_revisits_processed"
CONFIG_DIR="$PWD/config"

# poetry run create <document> [--new] <data_directory> <chunks>
poetry run create "$PROJECT_DIR/qd61g27j_script.psz" --new "$DATA_DIR" "$CONFIG_DIR/chunks/qd61g27j.toml"

exit 0
