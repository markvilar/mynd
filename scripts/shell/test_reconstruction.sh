#!/usr/bin/bash

DATA_DIR="/data/kingston_snv_01/"

PROJECT_DIR="${DATA_DIR}/acfr_revisits_metashape_projects"
PIPELINE_DIR="${PWD}/config"

PROJECT_FILE="qtqxshxs_unaligned_dev.psz"
PIPELINE_FILE="reconstruction.toml"

# "qd61g27j_working_version.psz"
# "qdc5ghs3_working_version.psz"
# "qdch0ftq_working_version.psz"
# "qdchdmy1_working_version.psz"

# poetry run reconstruct <project> <pipeline> [selection]
poetry run reconstruct "${PROJECT_DIR}/${PROJECT_FILE}" "${PIPELINE_DIR}/${PIPELINE_FILE}" \
  --select "qtqxshxs_20110815_102540" "qtqxshxs_20150327_015552"

exit 0
