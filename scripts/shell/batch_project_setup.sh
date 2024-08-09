#!/usr/bin/bash

DEVICE="/data/kingston_snv_01"

PROJECT_DIR="$DEVICE/acfr_revisits_metashape_projects_test"
DATA_DIR="$DEVICE"
CONFIG_DIR="$PWD/config"

declare -a SITES=(
  "qd61g27j"
  "qdc5ghs3"
  "qdch0ftq"
  "qdchdmy1"
  "qtqxshxs"
  "r7jjskxq"
  "r7jjss8n"
  "r7jjssbh"
  "r23m7ms0"
  "r29mrd5h"
  "r29mrd12"
  "r234xgje"
  "r23685bc"
)

for SITE in "${SITES[@]}"
do
  # poetry run create <document> [--new] <data_directory> <chunks>
  poetry run create "${PROJECT_DIR}/${SITE}_project_init.psz" --new \
    "$DATA_DIR" "$CONFIG_DIR/data_descriptors/${SITE}.toml"
done

exit 0
