#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects_dev"
OUTPUT_DIR="/data/kingston_snv_01/acfr_metashape_projects_registered"

CACHE="/data/kingston_snv_01/acfr_point_clouds"

HIGH_RES_CONFIG="config/register_highres.toml"
LOW_RES_CONFIG="config/register_lowres.toml"


poetry run mynd register \
  "${SOURCE_DIR}/r23m7ms0_dense_with_metadata.psz" \
  "${OUTPUT_DIR}/r23m7ms0_registered_with_metadata.psz" \
  "${LOW_RES_CONFIG}" \
  "${CACHE}" \
  --reference "r23m7ms0_20100606_001908"


poetry run mynd register \
  "${SOURCE_DIR}/r29mrd5h_dense_with_metadata.psz" \
  "${OUTPUT_DIR}/r29mrd5h_registered_with_metadata.psz" \
  "${LOW_RES_CONFIG}" \
  "${CACHE}" \
  --reference "r29mrd5h_20090612_225306"


poetry run mynd register \
  "${SOURCE_DIR}/r234xgje_dense_with_metadata.psz" \
  "${OUTPUT_DIR}/r234xgje_registered_with_metadata.psz" \
  "${LOW_RES_CONFIG}" \
  "${CACHE}" \
  --reference "r234xgje_20100604_230524"


poetry run mynd register \
  "${SOURCE_DIR}/r23685bc_dense_with_metadata.psz" \
  "${OUTPUT_DIR}/r23685bc_registered_with_metadata.psz" \
  "${LOW_RES_CONFIG}" \
  "${CACHE}" \
  --reference "r23685bc_20100605_021022"
