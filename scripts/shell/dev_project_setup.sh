#!/usr/bin/bash

DEVICE="/data/kingston_snv_01"

PROJECT_DIR="$DEVICE/acfr_revisits_metashape_projects_test"
DATA_DIR="$DEVICE"
CONFIG_DIR="$PWD/config"

declare -a SITES=(
  "qd61g27j"
)

for SITE in "${SITES[@]}"
do
  # poetry run create <document> [--new] <data_directory> <chunks>
  poetry run create "${PROJECT_DIR}/${SITE}_project_init.psz" --new "$DATA_DIR" "$CONFIG_DIR/chunks/${SITE}.toml"
done

exit 0
