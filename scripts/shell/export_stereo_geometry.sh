#!/usr/bin/bash

MODEL="./resources/hitnet_models/hitnet_eth3d_480x640.onnx"
DESTINATION="/data/kingston_snv_01/stereo_export"


SOURCE="/data/kingston_snv_01/acfr_metashape_projects/qdc5ghs3_aligned_with_metadata.psz"


declare -a TARGETS=(
  "qdc5ghs3_20100430_024508"
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
