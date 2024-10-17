#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="r29mrd12_without_metadata.psz"
DESTINATION_FILE="r29mrd12_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "r29mrd12_20090613_010853" \
    "${METADATA_DIR}/r29mrd12_20090613_010853_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r29mrd12_20090613_104954" \
    "${METADATA_DIR}/r29mrd12_20090613_104954_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r29mrd12_20110612_045149" \
    "${METADATA_DIR}/r29mrd12_20110612_045149_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "r29mrd12_20130611_015335" \
    "${METADATA_DIR}/r29mrd12_20130611_015335_cameras_metadata.csv" \
    "${CONFIG}"
