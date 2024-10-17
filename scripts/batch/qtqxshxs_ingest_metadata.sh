#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects"
DESTINATION_DIR="/data/kingston_snv_01/acfr_metashape_projects_metadata"

SOURCE_FILE="qtqxshxs_without_metadata.psz"
DESTINATION_FILE="qtqxshxs_with_metadata.psz"

CONFIG="config/metadata/acfr_cameras.toml"
METADATA_DIR="/data/kingston_snv_01/acfr_cameras_metadata"

SOURCE="${SOURCE_DIR}/${SOURCE_FILE}"
DESTINATION="${DESTINATION_DIR}/${DESTINATION_FILE}"


poetry run mynd ingest-metadata \
  "${SOURCE}" \
  "${DESTINATION}" \
  --bundle \
    "qtqxshxs_20110815_102540" \
    "${METADATA_DIR}/qtqxshxs_20110815_102540_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qtqxshxs_20150327_015552" \
    "${METADATA_DIR}/qtqxshxs_20150327_015552_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qtqxshxs_20150328_000850" \
    "${METADATA_DIR}/qtqxshxs_20150328_000850_cameras_metadata.csv" \
    "${CONFIG}" \
  --bundle \
    "qtqxshxs_20150328_042551" \
    "${METADATA_DIR}/qtqxshxs_20150328_042551_cameras_metadata.csv" \
    "${CONFIG}"
