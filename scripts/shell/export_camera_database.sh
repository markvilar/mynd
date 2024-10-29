#!/usr/bin/bash

TIMESTAMP_EXPORT=true
EXPORT_IMAGES=true

if ${TIMESTAMP_EXPORT}; then
  DATE=$(date "+%Y%m%d_%H%M%S")
else
  DATE=""
fi

# r23m7ms0_20100606_001908
# r29mrd5h r29mrd5h_20090613_100254
# r29mrd5h_20090613_100254
# r23685bc_20100605_021022

SOURCE="/data/kingston_snv_01/acfr_metashape_projects/qdchdmy1_aligned_with_metadata.psz"
DESTINATION="/data/kingston_snv_01/camera_export"

declare -a TARGETS=(
  "qdchdmy1_20110416_005411"
)


for TARGET in "${TARGETS[@]}"
do

  poetry run mynd export-cameras \
    "${SOURCE}" \
    "${DESTINATION}/${DATE}_${TARGET}_cameras.h5" \
    "${TARGET}"

done
