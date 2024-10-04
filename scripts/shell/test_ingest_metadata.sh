#!/usr/bin/bash


SOURCE="/home/martin/data/acfr_camera_metadata/r23685bc_20100605_021022_camera_metadata.csv"
CONFIG="/home/martin/dev/mynd/config/metadata/acfr_cameras.toml"

# NOTE: Optional target group
TARGET="r23685bc_20100605_021022"

poetry run mynd ingest-metadata "${SOURCE}" "${CONFIG}"
