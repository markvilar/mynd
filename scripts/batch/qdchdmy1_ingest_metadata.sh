#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="qdchdmy1_without_metadata.psz"
DESTINATION_FILE="qdchdmy1_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "qdchdmy1_20110416_005411" \
    "${METADATA_DIR}/qdchdmy1_20110416_005411_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdchdmy1_20120501_071203" \
    "${METADATA_DIR}/qdchdmy1_20120501_071203_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdchdmy1_20130406_081713" \
    "${METADATA_DIR}/qdchdmy1_20130406_081713_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdchdmy1_20140328_063358" \
    "${METADATA_DIR}/qdchdmy1_20140328_063358_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdchdmy1_20170525_234624" \
    "${METADATA_DIR}/qdchdmy1_20170525_234624_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdchdmy1_20210315_081519" \
    "${METADATA_DIR}/qdchdmy1_20210315_081519_cameras_metadata.csv" \
    "${CONFIG}"
