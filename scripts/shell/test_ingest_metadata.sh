#!/usr/bin/bash

SOURCE="/data/kingston_snv_01/acfr_metashape_projects_dev/r23685bc_lite_metadata.psz"
DESTINATION="/data/kingston_snv_01/acfr_metashape_projects_dev/r23685bc_lite_metadata.psz"
CONFIG="config/metadata/acfr_cameras.toml"

METADATA="/data/kingston_snv_01/acfr_cameras_metadata/r23685bc_20100605_021022_camera_metadata.csv"
TARGET="r23685bc_20100605_021022"


poetry run mynd ingest-metadata "${METADATA}" "${CONFIG}" \
  --source "${SOURCE}" \
  --destination "${DESTINATION}"


METADATA="/data/kingston_snv_01/acfr_cameras_metadata/r23685bc_20120530_233021_camera_metadata.csv"
TARGET="r23685bc_20120530_233021"

poetry run mynd ingest-metadata "${METADATA}" "${CONFIG}" \
  --source "${SOURCE}" \
  --destination "${DESTINATION}"


METADATA="/data/kingston_snv_01/acfr_cameras_metadata/r23685bc_20120530_233021_camera_metadata.csv"
TARGET="r23685bc_20120530_233021"

poetry run mynd ingest-metadata "${METADATA}" "${CONFIG}" \
  --source "${SOURCE}" \
  --destination "${DESTINATION}"
