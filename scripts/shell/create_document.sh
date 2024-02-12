#!/usr/bin/bash

ROOT=/media/martin/lacie/data/acfr_debug/r23685bc/

DEPLOYMENT=r20100605_021022_lanterns_15_deep

python main.py \
    $ROOT/$DEPLOYMENT/images \
    $ROOT/$DEPLOYMENT/20100605_021022_cameras.csv
