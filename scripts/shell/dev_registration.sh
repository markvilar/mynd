#!/usr/bin/bash

DATA_DIR="${HOME}/data/acfr_revisits_metashape_projects_working"
DOCUMENT="${DATA_DIR}/qdc5ghs3_filtered.psz"

poetry run register "${DOCUMENT}" "${1}"
