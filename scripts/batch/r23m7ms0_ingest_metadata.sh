#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="r23m7ms0_without_metadata.psz"
DESTINATION_FILE="r23m7ms0_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "r23m7ms0_20100606_001908" \
    "${METADATA_DIR}/r23m7ms0_20100606_001908_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r23m7ms0_20120601_070118" \
    "${METADATA_DIR}/r23m7ms0_20120601_070118_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r23m7ms0_20140616_044549" \
    "${METADATA_DIR}/r23m7ms0_20140616_044549_cameras_metadata.csv" \
    "${CONFIG}"
