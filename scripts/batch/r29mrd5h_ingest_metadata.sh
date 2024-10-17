#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="r29mrd5h_without_metadata.psz"
DESTINATION_FILE="r29mrd5h_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "r29mrd5h_20090612_225306" \
    "${METADATA_DIR}/r29mrd5h_20090612_225306_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r29mrd5h_20090613_100254" \
    "${METADATA_DIR}/r29mrd5h_20090613_100254_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r29mrd5h_20110612_033752" \
    "${METADATA_DIR}/r29mrd5h_20110612_033752_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r29mrd5h_20130611_002419" \
    "${METADATA_DIR}/r29mrd5h_20130611_002419_cameras_metadata.csv" \
    "${CONFIG}"
