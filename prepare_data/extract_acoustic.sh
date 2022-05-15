#!/bin/bash

##################
### Define variables
####################################################################################

# Configuration directories
MARY_CONFIG_TEMPLATE=$PWD/configurations/training_config_template.json

# Input directories
ROOT_DIR=$PWD/../src/train
LIST_DIR=$ROOT_DIR/lists
OUTPUT_DIR=$PWD/output/acoustic/
ALL_SETS=(train val test)


##################
### Prepare environment
####################################################################################

# Extract raw coefficients
for cur_set in ${ALL_SETS[@]}
do
    cur_output_dir=$OUTPUT_DIR/wavegan/raw/$cur_set
    mkdir -p $cur_output_dir

    cat $LIST_DIR/${cur_set}.scp | \
        xargs -I {} -P 5 python scripts/extract_parameters.py \
              -v -c ./configurations/spect_extract.yaml \
              ../src/${cur_set}/wav/{}.wav $cur_output_dir
done

# Normalize
cur_input_dir=$OUTPUT_DIR/wavegan/raw/train
cur_output_dir=$OUTPUT_DIR/wavegan/norm/train
mkdir -p $cur_output_dir
python scripts/normalize_spect.py -L $LIST_DIR/train.scp $cur_input_dir $cur_output_dir

# TODO: add normalize for test and validation

# TODO: add wavenet conversion

# Extract F0
for cur_set in ${ALL_SETS[@]}
do
    cur_output_dir=$OUTPUT_DIR/f0
    mkdir -p $cur_output_dir

    cat $LIST_DIR/${cur_set}.scp | \
        xargs -I {} -P 5 python scripts/extract_f0.py -v \
              ../src/${cur_set}/wav/{}.wav $cur_output_dir/{}.f0
done
