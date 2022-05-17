#!/bin/bash

##################
### Define variables
####################################################################################

# Configuration directories
MARY_CONFIG_TEMPLATE=$PWD/configurations/training_config_template.json

# Input directories
CORPUS_ROOT_DIR=$PWD/../src/train
LIST_DIR=$CORPUS_ROOT_DIR/lists
OUTPUT_DIR=$PWD/output/acoustic/
ALL_SETS=(train val test)
VOCODERS=(wg wn)


##################
### Extract Spectrogram part
####################################################################################

# Extract using WaveGan scheme
echo "# =============================================================="
echo "# Extract WaveGAN spectrograms"
echo "# =============================================================="
for cur_set in ${ALL_SETS[@]}
do
    cur_output_dir=$OUTPUT_DIR/wg/raw/$cur_set
    mkdir -p $cur_output_dir

    cat $LIST_DIR/${cur_set}.scp | \
        xargs -I {} -P 5 python scripts/extract_spectrogram.py \
              -v -c ./configurations/param_wg.yaml \
              $CORPUS_ROOT_DIR/wav/{}.wav $cur_output_dir
done

# Now convert to wavenet!
echo "# =============================================================="
echo "# Convert WaveGAN spectrograms to WaveNet spectrograms (file type change!)"
echo "# =============================================================="
for cur_set in ${ALL_SETS[@]}
do
    cur_input_dir=$OUTPUT_DIR/wg/raw/$cur_set
    cur_output_dir=$OUTPUT_DIR/wn/raw/$cur_set
    mkdir -p $cur_output_dir
    python scripts/convert_spectrogram.py \
           -v -i wg -o wn \
           $cur_input_dir $cur_output_dir
done

##################
### Extract Wave
####################################################################################


for cur_voc in ${VOCODERS[@]}
do
    # Now convert to wavenet!
    echo "# =============================================================="
    echo "# Parametrize the waveform to be compatible with the vocoder \"${cur_voc}\""
    echo "# =============================================================="

    for cur_set in ${ALL_SETS[@]}
    do
        cur_output_dir=$OUTPUT_DIR/${cur_voc}/raw/$cur_set
        mkdir -p $cur_output_dir

        cat $LIST_DIR/${cur_set}.scp | \
            xargs -I {} -P 5 python scripts/parametrize_wav.py \
                  -t $cur_voc \
                  -v -c ./configurations/param_${cur_voc}.yaml \
                  $CORPUS_ROOT_DIR/wav/{}.wav $cur_output_dir
    done
done

exit 0

##################
### Normalize
####################################################################################

# Normalize
cur_input_dir=$OUTPUT_DIR/wavegan/raw/train
cur_output_dir=$OUTPUT_DIR/wavegan/norm/train
mkdir -p $cur_output_dir
python scripts/normalize_spect.py -L $LIST_DIR/train.scp $cur_input_dir $cur_output_dir

# TODO: add normalize for test and validation

# TODO: add wavenet conversion


##################
### Extract F0 for FastPitch
####################################################################################
for cur_set in ${ALL_SETS[@]}
do
    cur_output_dir=$OUTPUT_DIR/f0
    mkdir -p $cur_output_dir

    cat $LIST_DIR/${cur_set}.scp | \
        xargs -I {} -P 5 python scripts/extract_f0.py -v \
              ../src/${cur_set}/wav/{}.wav $cur_output_dir/{}.f0
done
