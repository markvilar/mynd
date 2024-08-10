#!/usr/bin/bash

DATA_DIR="/data/kingston_snv_01/acfr_revisits_metashape_projects"
# DATA_DIR="${HOME}/data/acfr_revisits_metashape_projects_working"
DOCUMENT="${DATA_DIR}/qdc5ghs3_working_version.psz"

poetry run register "${DOCUMENT}"
