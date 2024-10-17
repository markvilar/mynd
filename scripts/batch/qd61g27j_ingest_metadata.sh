#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="qd61g27j_without_metadata.psz"
DESTINATION_FILE="qd61g27j_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "qd61g27j_20100421_022145" \
    "${METADATA_DIR}/qd61g27j_20100421_022145_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qd61g27j_20110410_011202" \
    "${METADATA_DIR}/qd61g27j_20110410_011202_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qd61g27j_20120422_043114" \
    "${METADATA_DIR}/qd61g27j_20120422_043114_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qd61g27j_20130414_013620" \
    "${METADATA_DIR}/qd61g27j_20130414_013620_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qd61g27j_20170523_040815" \
    "${METADATA_DIR}/qd61g27j_20170523_040815_cameras_metadata.csv" \
    "${CONFIG}"
