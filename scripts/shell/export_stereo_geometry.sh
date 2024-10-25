#!/usr/bin/bash

MODEL="./resources/hitnet_models/hitnet_eth3d_480x640.onnx"
SOURCE="/data/kingston_snv_01/acfr_metashape_projects/r29mrd5h_aligned_with_metadata.psz"
DESTINATION="/data/kingston_snv_01/stereo_export"

declare -a TARGETS=(
  "r29mrd5h_20090612_225306"
  "r29mrd5h_20090613_100254"
  "r29mrd5h_20110612_033752"
  "r29mrd5h_20130611_002419"
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
