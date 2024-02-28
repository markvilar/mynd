#!/usr/bin/bash

PROJECT_DIR=/media/martin/lacie/data/acfr_metashape_projects
DATA_DIR=/media/martin/lacie/data/acfr_processed_simple
CONFIG_DIR=./config

SITE=qdc5ghs3

python add_chunk.py \
    $PROJECT_DIR/qdc5ghs3_script_test.psz \
    $DATA_DIR/$SITE/r20100430_024508_coralpatches_23_40m/images \
    $DATA_DIR/$SITE/r20100430_024508_coralpatches_23_40m/20100430_024508_cameras.csv \
    $CONFIG_DIR/stereo.toml

python add_chunk.py \
    $PROJECT_DIR/qdc5ghs3_script_test.psz \
    $DATA_DIR/$SITE/r20120501_033336_coralpatches_39_40m_out/images \
    $DATA_DIR/$SITE/r20120501_033336_coralpatches_39_40m_out/20120501_033336_cameras.csv \
    $CONFIG_DIR/stereo.toml

python add_chunk.py \
    $PROJECT_DIR/qdc5ghs3_script_test.psz \
    $DATA_DIR/$SITE/r20130405_103429_coralpatches_02_40m_out/images \
    $DATA_DIR/$SITE/r20130405_103429_coralpatches_02_40m_out/20130405_103429_cameras.csv \
    $CONFIG_DIR/stereo.toml

python add_chunk.py \
    $PROJECT_DIR/qdc5ghs3_script_test.psz \
    $DATA_DIR/$SITE/r20210315_230947_SS13_coralpatches_40m_out/images \
    $DATA_DIR/$SITE/r20210315_230947_SS13_coralpatches_40m_out/20210315_230947_cameras.csv \
    $CONFIG_DIR/stereo.toml
