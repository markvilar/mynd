#!/usr/bin/bash

MODEL="./resources/hitnet_models/hitnet_eth3d_480x640.onnx"
SOURCE="/data/kingston_snv_01/acfr_metashape_projects/r23m7ms0_aligned_with_metadata.psz"
DESTINATION="/data/kingston_snv_01/stereo_export"

declare -a TARGETS=(
  # "r23m7ms0_20100606_001908"
  "r23m7ms0_20120601_070118"
  "r23m7ms0_20140616_044549"
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
