#!/usr/bin/bash

TIMESTAMP_EXPORT=true
EXPORT_IMAGES=true

if ${TIMESTAMP_EXPORT}; then
  DATE=$(date "+%Y%m%d_%H%M%S")
else
  DATE=""
fi

# qdc5ghs3 qdc5ghs3_20100430_024508
# qdch0ftq qdch0ftq_20100428_020202
# qdchdmy1 qdchdmy1_20110416_005411
# r7jjskxq r7jjskxq_20101023_210332
# r23m7ms0 r23m7ms0_20100606_001908
# r29mrd5h r29mrd5h_20090613_100254
# r234xgje r234xgje_20100604_230524
# r23685bc r23685bc_20100605_021022

SOURCE="/data/kingston_snv_01/acfr_metashape_projects/qdc5ghs3_aligned_with_metadata.psz"
DESTINATION="/data/kingston_snv_01/acfr_camera_databases"

declare -a TARGETS=(
  "qdc5ghs3_20100430_024508"
)


for TARGET in "${TARGETS[@]}"
do

  poetry run mynd export-cameras \
    "${SOURCE}" \
    "${DESTINATION}/${TARGET}_cameras.asdf" \
    "${TARGET}"

done
