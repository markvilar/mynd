#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="r23685bc_without_metadata.psz"
DESTINATION_FILE="r23685bc_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "r23685bc_20100605_021022" \
    "${METADATA_DIR}/r23685bc_20100605_021022_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r23685bc_20120530_233021" \
    "${METADATA_DIR}/r23685bc_20120530_233021_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r23685bc_20140616_225022" \
    "${METADATA_DIR}/r23685bc_20140616_225022_cameras_metadata.csv" \
    "${CONFIG}"
