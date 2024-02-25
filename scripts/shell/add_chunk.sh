#!/usr/bin/bash

PROJECT_DIR=/home/martin/data/metashape_projects
DATA_DIR=/home/martin/data/acfr_debug/r23685bc
CONFIG_DIR=./config

python add_chunk.py \
    $PROJECT_DIR/r23685bc_script_test.psz \
    $DATA_DIR/r20100605_021022_lanterns_15_deep/images \
    $DATA_DIR/r20100605_021022_lanterns_15_deep/20100605_021022_cameras.csv \
    $CONFIG_DIR/stereo.toml

exit 0

python add_chunk.py \
    $PROJECT_DIR/r23685bc_script_test.psz \
    $DATA_DIR/r20120530_233021_lanterns_10_deep/images \
    $DATA_DIR/r20120530_233021_lanterns_10_deep/20120530_233021_cameras.csv \
    $CONFIG_DIR/stereo.toml

python add_chunk.py \
    $PROJECT_DIR/r23685bc_script_test.psz \
    $DATA_DIR/r20140616_225022_tas_13_lanterns_deep/images \
    $DATA_DIR/r20140616_225022_tas_13_lanterns_deep/20140616_225022_cameras.csv \
    $CONFIG_DIR/stereo.toml
