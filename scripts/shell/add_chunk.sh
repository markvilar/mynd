#!/usr/bin/bash

PROJECT_DIR=/home/martin/data/metashape_projects
DATA_DIR=/home/martin/data/acfr_debug/r23685bc
CONFIG_DIR=./config

poetry run create /home/martin/workspace/metashape_projects/r23685bc_script.psz --new


    # $DATA_DIR/20100605_021022/images \
    # $DATA_DIR/20100605_021022/20100605_021022_cameras.csv \
    # $CONFIG_DIR/stereo.toml \
    # 20100605_021022

exit 0

poetry run create \
    $PROJECT_DIR/r23685bc_script_test.psz \
    $DATA_DIR/20120530_233021/images \
    $DATA_DIR/20120530_233021/20120530_233021_cameras.csv \
    $CONFIG_DIR/stereo.toml \
    20120530_233021

poetry run create \
    $PROJECT_DIR/r23685bc_script_test.psz \
    $DATA_DIR/20140616_225022/images \
    $DATA_DIR/20140616_225022/20140616_225022_cameras.csv \
    $CONFIG_DIR/stereo.toml


exit 0

poetry run create \
  --document "/path/to/document.psz" \
  --chunks "/path/to/config" 

poetry run create --document "/path/to/document.psz" --new
