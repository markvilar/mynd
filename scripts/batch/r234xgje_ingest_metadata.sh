#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="r234xgje_without_metadata.psz"
DESTINATION_FILE="r234xgje_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "r234xgje_20100604_230524" \
    "${METADATA_DIR}/r234xgje_20100604_230524_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r234xgje_20120530_064545" \
    "${METADATA_DIR}/r234xgje_20120530_064545_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r234xgje_20140616_205232" \
    "${METADATA_DIR}/r234xgje_20140616_205232_cameras_metadata.csv" \
    "${CONFIG}"
