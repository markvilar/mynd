#!/usr/bin/bash

TIMESTAMP_EXPORT=true
EXPORT_IMAGES=true

if ${TIMESTAMP_EXPORT}; then
  DATE=$(date "+%Y%m%d_%H%M%S")
else
  DATE=""
fi


SOURCE="/data/kingston_snv_01/acfr_metashape_projects/r23m7ms0_aligned_with_metadata.psz"
DESTINATION="/data/kingston_snv_02/acfr_camera_database"

declare -a TARGETS=(
  "r23m7ms0_20100606_001908"
  "r23m7ms0_20120601_070118"
  "r23m7ms0_20140616_044549"
)


for TARGET in "${TARGETS[@]}"
do

  COLOR_DIR="/data/kingston_snv_02/acfr_images_debayered/${TARGET}_debayered/"
  RANGE_DIR="/data/kingston_snv_01/acfr_stereo_geometry/${TARGET}_ranges/"
  NORMAL_DIR="/data/kingston_snv_01/acfr_stereo_geometry/${TARGET}_normals/"

  poetry run mynd export-cameras \
    "${SOURCE}" \
    "${DESTINATION}/${TARGET}_cameras.h5" \
    "${TARGET}" \
    --colors "${COLOR_DIR}" \
    --ranges "${RANGE_DIR}" \
    --normals "${NORMAL_DIR}"

done
