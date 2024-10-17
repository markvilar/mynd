#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="qdc5ghs3_without_metadata.psz"
DESTINATION_FILE="qdc5ghs3_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "qdc5ghs3_20100430_024508" \
    "${METADATA_DIR}/qdc5ghs3_20100430_024508_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdc5ghs3_20120501_033336" \
    "${METADATA_DIR}/qdc5ghs3_20120501_033336_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdc5ghs3_20130405_103429" \
    "${METADATA_DIR}/qdc5ghs3_20130405_103429_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdc5ghs3_20210315_230947" \
    "${METADATA_DIR}/qdc5ghs3_20210315_230947_cameras_metadata.csv" \
    "${CONFIG}"
