#!/bin/bash

##################
### Define options
####################################################################################
: ${NUM_CPUS:=4}
: ${VERBOSE:=0}

[ "$VERBOSE" == "1" ] && VERB_FLAG="-v"
[ "$VERBOSE" == "2" ] && VERB_FLAG="-vv"


##################
### Define Constants
####################################################################################

# Input directories
CORPUS_ROOT_DIR=$PWD/../src/train
LIST_DIR=$CORPUS_ROOT_DIR/lists
OUTPUT_DIR=$PWD/output/training
ALL_SETS=(train val test)
VOCODERS=(wg wn)
ACOUSTIC_MODEL_TOOLKITS=(fastpitch tacotron)

##################
### Extract Spectrogram in WaveGAN Format
####################################################################################

echo "# =============================================================="
echo "# Extract WaveGAN spectrograms"
echo "# =============================================================="
for cur_set in ${ALL_SETS[@]}
do
    cur_output_dir=$OUTPUT_DIR/wg/raw/$cur_set
    mkdir -p $cur_output_dir

    cat $LIST_DIR/${cur_set}.scp | \
        xargs -I {} -P $NUM_CPUS python scripts/extract_spectrogram.py \
              $VERB_FLAG -c ./configurations/param_wg.yaml \
              $CORPUS_ROOT_DIR/wav/{}.wav $cur_output_dir
done

##################
### Normalize (NOTE: only wavegan/wavenet supported)
####################################################################################

echo "# =============================================================="
echo "# Compute scaler on WaveGAN"
echo "# =============================================================="

# Normalize
cur_input_dir=$OUTPUT_DIR/wg/raw/train
python scripts/compute_scaler.py $VERB_FLAG -t wg $cur_input_dir $OUTPUT_DIR/wg/stats.h5


echo "# =============================================================="
echo "# Normalize WaveGAN spectrogram features"
echo "# =============================================================="
for cur_set in ${ALL_SETS[@]}
do
    cur_input_dir=$OUTPUT_DIR/wg/raw/$cur_set
    cur_output_dir=$OUTPUT_DIR/wg/norm/$cur_set
    mkdir -p $cur_output_dir
    python scripts/normalize_spect.py \
           $VERB_FLAG $OUTPUT_DIR/wg/stats.h5 \
           $cur_input_dir $cur_output_dir
done

##################
### Convert WaveGAN feats + scaler to WaveNet
####################################################################################

echo "# =============================================================="
echo "# Convert WaveGAN spectrograms to other toolkits spectrograms (file type change!)"
echo "# =============================================================="

for cur_voc in ${VOCODERS[@]:1}
do
    for cur_set in ${ALL_SETS[@]}
    do
        cur_input_dir=$OUTPUT_DIR/wg/norm/$cur_set
        cur_output_dir=$OUTPUT_DIR/${cur_voc}/norm/$cur_set
        mkdir -p $cur_output_dir
        python scripts/convert_spectrogram.py \
               $VERB_FLAG -i wg -o ${cur_voc} \
               $cur_input_dir $cur_output_dir
    done
done

for cur_tk in ${ACOUSTIC_MODEL_TOOLKITS[@]}
do
    for cur_set in ${ALL_SETS[@]}
    do
        cur_input_dir=$OUTPUT_DIR/wg/norm/$cur_set
        cur_output_dir=$OUTPUT_DIR/${cur_tk}/mel/
        mkdir -p $cur_output_dir
        python scripts/convert_spectrogram.py \
               $VERB_FLAG -i wg -o ${cur_tk} \
               $cur_input_dir $cur_output_dir
    done
done

##################
### Extract Wave
####################################################################################

for cur_voc in ${VOCODERS[@]}
do
    echo "# =============================================================="
    echo "# Parametrize the waveform to be compatible with the vocoder \"${cur_voc}\""
    echo "# =============================================================="

    for cur_set in ${ALL_SETS[@]}
    do
        cur_output_dir=$OUTPUT_DIR/${cur_voc}/norm/$cur_set
        mkdir -p $cur_output_dir

        cat $LIST_DIR/${cur_set}.scp | \
            xargs -I {} -P $NUM_CPUS python scripts/parametrize_wav.py \
                  -t $cur_voc \
                  $VERB_FLAG -c ./configurations/param_${cur_voc}.yaml \
                  $CORPUS_ROOT_DIR/wav/{}.wav $cur_output_dir
    done
done


##################
### Extract F0 (at frame level) for FastPitch
####################################################################################

echo "# =============================================================="
echo "# Extract F0 at frame (frameshift = 5ms) horizon"
echo "# =============================================================="

for cur_set in ${ALL_SETS[@]}
do
    cur_output_dir=$OUTPUT_DIR/f0
    mkdir -p $cur_output_dir

    cat $LIST_DIR/${cur_set}.scp | \
        xargs -I {} -P $NUM_CPUS python scripts/extract_f0.py $VERB_FLAG \
              ../src/train/wav/{}.wav $cur_output_dir/{}.f0
done
