#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="qdch0ftq_without_metadata.psz"
DESTINATION_FILE="qdch0ftq_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"

poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "qdch0ftq_20100428_020202" \
    "${METADATA_DIR}/qdch0ftq_20100428_020202_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdch0ftq_20110415_020103" \
    "${METADATA_DIR}/qdch0ftq_20110415_020103_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdch0ftq_20120430_002423" \
    "${METADATA_DIR}/qdch0ftq_20120430_002423_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdch0ftq_20130406_023610" \
    "${METADATA_DIR}/qdch0ftq_20130406_023610_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdch0ftq_20140327_071251" \
    "${METADATA_DIR}/qdch0ftq_20140327_071251_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdch0ftq_20170526_025746" \
    "${METADATA_DIR}/qdch0ftq_20170526_025746_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qdch0ftq_20210315_034028" \
    "${METADATA_DIR}/qdch0ftq_20210315_034028_cameras_metadata.csv" \
    "${CONFIG}"
