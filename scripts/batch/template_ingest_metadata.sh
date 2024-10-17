#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="SITE_without_metadata.psz"
DESTINATION_FILE="SITE_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "SITE_VISIT_01" \
    "${METADATA_DIR}/SITE_VISIT_01_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "SITE_VISIT_02" \
    "${METADATA_DIR}/SITE_VISIT_02_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "SITE_VISIT_03" \
    "${METADATA_DIR}/SITE_VISIT_03_cameras_metadata.csv" \
    "${CONFIG}"
