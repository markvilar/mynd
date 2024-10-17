#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="r7jjss8n_without_metadata.psz"
DESTINATION_FILE="r7jjss8n_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "r7jjss8n_20101023_210332" \
    "${METADATA_DIR}/r7jjss8n_20101023_210332_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r7jjss8n_20121013_060425" \
    "${METADATA_DIR}/r7jjss8n_20121013_060425_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r7jjss8n_20131022_004934" \
    "${METADATA_DIR}/r7jjss8n_20131022_004934_cameras_metadata.csv" \
    "${CONFIG}"
