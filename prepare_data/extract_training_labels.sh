#!/bin/bash

##################
### Define variables
####################################################################################

# Configuration directories
MARY_CONFIG_TEMPLATE=$PWD/configurations/training_config_template.json

# Input directories
ROOT_DIR=$PWD/../src/train
LIST_DIR=$ROOT_DIR/lists
F0_DIR=$ROOT_DIR/f0
ALL_SETS=(train val test)

# Output directories
FASTPITCH_DIR=$PWD/output/training_fastpitch
FASTPITCH_DUR_DIR=$FASTPITCH_DIR/dur
FASTPITCH_F0_DIR=$FASTPITCH_DIR/f0
FASTPITCH_FILELIST_DIR=$FASTPITCH_DIR/filelists

TACOTRON_DIR=$PWD/output/training/tacotron
TACOTRON_DUR_DIR=$TACOTRON_DIR/dur
TACOTRON_FILELIST_DIR=$TACOTRON_DIR/filelists

# TMP_STUFFY
TMP_DIR=$TMP/tmp
LABEL_DIR=$TMP_DIR/labels
RAW_F0_DIR=$TMP_DIR/raw_f0
VALID_LIST_DIR=$TMP_DIR/valid_lists
MARY_CONFIG=$TMP_DIR/mary_config.json

##################
### Prepare environment
####################################################################################

mkdir -p $RAW_F0_DIR $VALID_LIST_DIR $LABEL_DIR
mkdir -p $FASTPITCH_F0_DIR $FASTPITCH_FILELIST_DIR $FASTPITCH_DUR_DIR
mkdir -p $TACOTRON_FILELIST_DIR $TACOTRON_DUR_DIR


##################
### Generate labels using MaryTTS and Kaldi
####################################################################################

sed "s%### TRAIN_DIR ###%$ROOT_DIR%g" $MARY_CONFIG_TEMPLATE > $MARY_CONFIG
(
    cd $PWD/../toolkits/marytts/hts-label-generation;
    ./gradlew b --max-workers=30 -Dconfig=$MARY_CONFIG \
        --include-build=../marytts \
        --include-build=../gradle-marytts-kaldi-mfa-plugin \
        --include-build=../gradle-marytts-align-plugin \
        --include-build=../gradle-marytts-dict-extraction \
        --no-daemon \
        --stacktrace;
)

cp -fv $PWD/../toolkits/marytts/hts-label-generation/build/hts_labels/mono/*.lab $LABEL_DIR


##################
### Generate generic prompt
####################################################################################

# List files that merlin was able to process
comm -12 \
     <(ls -1 $LABEL_DIR/*.lab | xargs -I {} basename {} .lab | sort -u)\
     <(ls -1 $F0_DIR/*.f0 | xargs -I {} basename {} .f0 | sort -u) |
    sed 's/^[ \t]*//g' > $TMP_DIR/merlin_valid_list.scp

# Generate prompt
cat $TMP_DIR/merlin_valid_list.scp | \
    xargs -I {} awk -f scripts/generate_prompt.awk $LABEL_DIR/{}.lab > $TMP_DIR/ph_prompt.gui

##################
### Generate FastPitch data (F0, duration & prompts)
####################################################################################

# Generate the coefficient files needed for fastpitch
cat $TMP_DIR/merlin_valid_list.scp | \
    parallel --verbose -I {} python scripts/convert.py \
             $LABEL_DIR/{}.lab \
             $F0_DIR/{}.f0 \
             $FASTPITCH_DUR_DIR/{}.pt \
             $RAW_F0_DIR/{}.pt

# Filter training set files and normalize
for cur_set in ${ALL_SETS[@]}
do
    # Filter
    comm -12 <(sort -u $LIST_DIR/${cur_set}.scp) $TMP_DIR/merlin_valid_list.scp > $VALID_LIST_DIR/${cur_set}.scp

    # Normalize F0
    python scripts/normalize_f0.py $VALID_LIST_DIR/${cur_set}.scp \
           $RAW_F0_DIR $FASTPITCH_F0_DIR \
           $FASTPITCH_DIR/pitch_char_stats__bc_2013_audio_text_${cur_set}_filelist.json

    # deal with the prompt
    python scripts/generate_nvidia_prompts.py -f fastpitch $TMP_DIR/ph_prompt.gui \
           "$LIST_DIR/${cur_set}.scp" \
           $FASTPITCH_FILELIST_DIR/bc_2013_mel_dur_pitch_text_${cur_set}_filelist.txt
done

# Generate list of symbols
cat $FASTPITCH_FILELIST_DIR/bc_2013_mel_dur_pitch_text_train_filelist.txt | \
    cut -d '|' -f4 | tr ' ' $'\n' | sort -u > $FASTPITCH_DIR/ph_list


##################
### Generate Tacotron prompt & attention
####################################################################################

# Filter training set files and normalize
for cur_set in ${ALL_SETS[@]}
do
    # Filter
    comm -12 <(sort -u $LIST_DIR/${cur_set}.scp) $TMP_DIR/merlin_valid_list.scp > $VALID_LIST_DIR/${cur_set}.scp

    # deal with the prompt
    python scripts/generate_nvidia_prompts.py -f tacotron $TMP_DIR/ph_prompt.gui \
           "$LIST_DIR/${cur_set}.scp" \
           $TACOTRON_FILELIST_DIR/metadata_${cur_set}.psv
done

# Generate list of symbols
cat $TACOTRON_FILELIST_DIR/metadata_train.psv | cut -d '|' -f4 |tr ' ' $'\n'| sort -u > $TACOTRON_DIR/ph_list
