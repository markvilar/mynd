#!/usr/bin/bash

SOURCE="/data/kingston_snv_01/acfr_revisits_metashape_dev/r23685bc_lite_version.psz"
DESTINATION="/data/kingston_snv_01/camera_export/r23685bc_camera.h5"

TARGET="r23685bc_20100605_021022"

IMAGE_DIR="/data/kingston_snv_02/acfr_images_preprocessed/r23685bc_20100605_021022_images/"
RANGE_DIR="/data/kingston_snv_01/acfr_stereo_ranges/r23685bc_20100605_021022_ranges/"
NORMAL_DIR="/data/kingston_snv_01/acfr_stereo_normals/r23685bc_20100605_021022_normals/"

poetry run mynd export-cameras "${SOURCE}" "${DESTINATION}" "${TARGET}" \
  --images "${IMAGE_DIR}" \
  --ranges "${RANGE_DIR}" \
  --normals "${NORMAL_DIR}"
