#!/usr/bin/bash

TIMESTAMP_EXPORT=true
EXPORT_IMAGES=true

if ${TIMESTAMP_EXPORT}; then
  DATE=$(date "+%Y%m%d_%H%M%S")
else
  DATE=""
fi

SOURCE="/data/kingston_snv_01/acfr_revisits_metashape_dev/r23685bc_lite_version.psz"
DESTINATION="/data/kingston_snv_01/camera_export/${DATE}_r23685bc_cameras.h5"

TARGET="r23685bc_20100605_021022"

COLOR_DIR="/data/kingston_snv_02/acfr_images_preprocessed/r23685bc_20100605_021022_images/"
RANGE_DIR="/data/kingston_snv_01/acfr_stereo_ranges/r23685bc_20100605_021022_ranges/"
NORMAL_DIR="/data/kingston_snv_01/acfr_stereo_normals/r23685bc_20100605_021022_normals/"


if $EXPORT_IMAGES; then
  poetry run mynd export-cameras "${SOURCE}" "${DESTINATION}" "${TARGET}" \
    --colors "${COLOR_DIR}" \
    --ranges "${RANGE_DIR}" \
    --normals "${NORMAL_DIR}"
else
  poetry run mynd export-cameras "${SOURCE}" "${DESTINATION}" "${TARGET}"
fi
