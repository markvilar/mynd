#!/usr/bin/bash

SOURCE_DIR="/data/kingston_snv_01/acfr_metashape_projects_dev"
OUTPUT_DIR="/data/kingston_snv_01/acfr_metashape_projects_registered"

CACHE="/data/kingston_snv_01/acfr_point_clouds"

HIGH_RES_CONFIG="config/register_highres.toml"
LOW_RES_CONFIG="config/register_lowres.toml"


SITE="qdch0ftq"
REFERENCE="qdch0ftq_20100428_020202"


poetry run mynd register \
  "${SOURCE_DIR}/${SITE}_dense_with_metadata.psz" \
  "${OUTPUT_DIR}/${SITE}_registered_with_metadata.psz" \
  "${HIGH_RES_CONFIG}" \
  "${CACHE}" \
  --reference "${REFERENCE}" \
  --vis
