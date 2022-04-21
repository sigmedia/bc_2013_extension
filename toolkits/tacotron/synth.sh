#!/bin/bash

# =====================================================================
# Dealing with configuration
# =====================================================================
# Global
: ${NB_PROCS:=16}

# Fast Pitch
: ${EPOCH:=1500}
: ${EXP_DIR:=$PWD/bc_2013}
: ${PH_DICT:=None}
: ${IMPOSE_DUR:=None}

# WaveNET
: ${WAVENET_EXP_DIR:=$HOME/work/neural_vocoders/wavenet/egs/mol_wg/}
: ${WAVENET_EXP_ID:=bc_2013_orig}
: ${BS:=32}

# WaveGAN
: ${WAVEGAN_EXP_DIR:=$HOME/work/neural_vocoders/ParallelWaveGAN/egs/bc_2013/voc1/}
: ${WG_STEPS:=1290000}

TEST_FILE=$1

# Current Experiment
EXP_DIR=$(realpath $EXP_DIR) # NOTE: need actual absolute path for wavegan
export MEL_DIR=$EXP_DIR/mel
export WAVENET_OUTPUT_DIR=$EXP_DIR/wavenet
export WAVEGAN_OUTPUT_DIR=$EXP_DIR/wavegan

# =====================================================================
# Generate Mel Spectrograms
# =====================================================================

mkdir -p $MEL_DIR

[ "$PH_DICT" != "None" ] && SYMBOL_OPT="--symbol-dict $PH_DICT"

python gen_tacotron.py \
    --symbol-dict bc_2013/ph_list \
    --hp_file hparams.py \
    --save_attention \
    -O $MEL_DIR \
    -I $TEST_FILE \
    none


# =====================================================================
# Rendering using WaveNET
# =====================================================================
# Convert FP spectrogram to wavenet
mkdir -p $WAVENET_OUTPUT_DIR
tail -n +2 $TEST_FILE |
	cut -d$'\t' -f1 |
	xargs -P $NB_PROCS -n 1 -I {} python tacotron2voc.py -v --voc wn $MEL_DIR/{}.npy $WAVENET_OUTPUT_DIR/{}-feats.npy

# Rendering
python ~/work/neural_vocoders/wavenet/evaluate.py \
	$WAVENET_OUTPUT_DIR \
	$WAVENET_EXP_DIR/exp/${WAVENET_EXP_ID}_train_no_dev_mol_wavenet/checkpoint_latest.pth \
	$WAVENET_OUTPUT_DIR \
	--preset $WAVENET_EXP_DIR/exp/${WAVENET_EXP_ID}_train_no_dev_mol_wavenet/hparams.json \
	--hparams="batch_size=${BS}"

# =====================================================================
# Rendering using WaveGAN
# =====================================================================

# Convert FP spectrogram to wavegan
mkdir -p $WAVEGAN_OUTPUT_DIR
tail -n +2 $TEST_FILE |
	cut -d$'\t' -f1 |
	xargs -P $NB_PROCS -n 1 -I {} python tacotron2voc.py -v --voc wg $MEL_DIR/{}.npy $WAVEGAN_OUTPUT_DIR/{}.h5

# Rendering
(
	cd $WAVEGAN_EXP_DIR
	. ./cmd.sh || exit 1
	. ./path.sh || exit 1

	${cuda_cmd} --gpu "1" /dev/stdout \
		parallel-wavegan-decode \
		--dumpdir "$WAVEGAN_OUTPUT_DIR" \
		--checkpoint $WAVEGAN_EXP_DIR/exp/train_nodev_parallel_wavegan.v1/checkpoint-${WG_STEPS}steps.pkl \
		--outdir "$WAVEGAN_OUTPUT_DIR" \
		--verbose "1" | tee "$WAVEGAN_OUTPUT_DIR/decode.log"
)
