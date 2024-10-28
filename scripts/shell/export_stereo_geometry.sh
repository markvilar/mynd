#!/usr/bin/bash

MODEL="./resources/hitnet_models/hitnet_eth3d_480x640.onnx"
SOURCE="/data/kingston_snv_01/acfr_metashape_projects/r7jjskxq_aligned_with_metadata.psz"
DESTINATION="/data/kingston_snv_01/stereo_export"


declare -a TARGETS=(
  "r7jjskxq_20101023_210332"
  "r7jjskxq_20121013_060425"
  "r7jjskxq_20131022_004934"
)


for TARGET in "${TARGETS[@]}"
do
  poetry run mynd export-stereo \
    "${SOURCE}" \
    "${DESTINATION}" \
    "${MODEL}" \
    "${TARGET}" \
    --save-samples
done

exit 0
