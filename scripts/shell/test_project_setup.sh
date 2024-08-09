#!/usr/bin/bash

DEVICE="/media/martin/pcie_01"

PROJECT_DIR="$DEVICE/acfr_revisits_metashape_projects_test"
DATA_DIR="$DEVICE"
CONFIG_DIR="$PWD/config"

# poetry run create <document> [--new] <data_directory> <chunks>
poetry run create "${PROJECT_DIR}/qd61g27j_project_init_mono.psz" --new \
  "$DATA_DIR" "$CONFIG_DIR/test_data_descriptors/qd61g27j_mono.toml"

poetry run create "${PROJECT_DIR}/qd61g27j_project_init_stereo.psz" --new \
  "$DATA_DIR" "$CONFIG_DIR/test_data_descriptors/qd61g27j_stereo.toml"

exit 0
