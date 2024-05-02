#!/usr/bin/bash

PROJECT_DIR=/home/martin/data/metashape_projects
DATA_DIR=/home/martin/data/acfr_debug/r23685bc
CONFIG_DIR=./config

poetry run add-chunk \
    $PROJECT_DIR/r23685bc_script_test.psz \
    $DATA_DIR/20100605_021022/images \
    $DATA_DIR/20100605_021022/20100605_021022_cameras.csv \
    $CONFIG_DIR/stereo.toml \
    20100605_021022

exit 0

python add_chunk.py \
    $PROJECT_DIR/r23685bc_script_test.psz \
    $DATA_DIR/20120530_233021/images \
    $DATA_DIR/20120530_233021/20120530_233021_cameras.csv \
    $CONFIG_DIR/stereo.toml

python add_chunk.py \
    $PROJECT_DIR/r23685bc_script_test.psz \
    $DATA_DIR/20140616_225022/images \
    $DATA_DIR/20140616_225022/20140616_225022_cameras.csv \
    $CONFIG_DIR/stereo.toml
