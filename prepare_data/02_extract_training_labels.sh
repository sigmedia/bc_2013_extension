#!/bin/bash

##################
### Define variables
####################################################################################

# Configuration directories
MARY_CONFIG_TEMPLATE=$PWD/configurations/training_config_template.json

# Input directories
CORPUS_ROOT_DIR=$PWD/../src/train
LIST_DIR=$CORPUS_ROOT_DIR/lists
ALL_SETS=(train val test)

# Output directories
OUTPUT_ROOT_DIR=$PWD/output/training
F0_DIR=$OUTPUT_ROOT_DIR/f0  # Actually an input but an output of the previous script, see 01_extract_acoustics.sh

#   - FastPitch directories
FASTPITCH_DIR=$OUTPUT_ROOT_DIR/fastpitch
FASTPITCH_DUR_DIR=$FASTPITCH_DIR/dur
FASTPITCH_F0_DIR=$FASTPITCH_DIR/f0
FASTPITCH_FILELIST_DIR=$FASTPITCH_DIR/filelists

#   - Tacotron directories
TACOTRON_DIR=$OUTPUT_ROOT_DIR/tacotron
TACOTRON_ATT_GUIDES_DIR=$TACOTRON_DIR/att_guides
TACOTRON_FILELIST_DIR=$TACOTRON_DIR/filelists

# TMP_STUFFY
TMP_DIR=$PWD/tmp/training
LABEL_DIR=$TMP_DIR/labels
RAW_F0_DIR=$TMP_DIR/raw_f0
VALID_LIST_DIR=$TMP_DIR/valid_lists
MARY_CONFIG=$TMP_DIR/mary_config.json

##################
### Prepare environment
####################################################################################

mkdir -p $RAW_F0_DIR $VALID_LIST_DIR $LABEL_DIR
mkdir -p $FASTPITCH_F0_DIR $FASTPITCH_FILELIST_DIR $FASTPITCH_DUR_DIR
mkdir -p $TACOTRON_FILELIST_DIR $TACOTRON_ATT_GUIDES

##################
### Generate labels using MaryTTS and Kaldi
####################################################################################

echo "# =============================================================="
echo "# Use MaryTTS to extract the labels"
echo "# =============================================================="

sed "s%### TRAIN_DIR ###%$CORPUS_ROOT_DIR%g" $MARY_CONFIG_TEMPLATE > $MARY_CONFIG
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

echo "# =============================================================="
echo "# Generate generic prompts from the extract labels"
echo "# =============================================================="

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

echo "# =============================================================="
echo "# Generate FastPitch data (F0, duration & prompts)"
echo "# =============================================================="

# Generate the coefficient files needed for fastpitch
cat $TMP_DIR/merlin_valid_list.scp | \
    parallel --verbose -I {} python scripts/merlin2fastpitch.py \
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

echo "# =============================================================="
echo "# Generate Tacotron data (prompt & attention guides)"
echo "# =============================================================="

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
cat $TACOTRON_FILELIST_DIR/metadata_train.psv | cut -d '|' -f2 | tr ' ' $'\n' |  sort -u > $TACOTRON_DIR/ph_list

# Generate attention guides
cat $TMP_DIR/merlin_valid_list.scp | \
    parallel --verbose -I {} python scripts/lab2att.py \
             $LABEL_DIR/{}.lab \
             $TACOTRON_ATT_GUIDES_DIR/{}.npy

# Generate PKL files
python scripts/generate_dataset_pkl.py --metadata $TACOTRON_FILELIST_DIR/metadata_train.psv  $TACOTRON_DIR/mel/ $TACOTRON_DIR
