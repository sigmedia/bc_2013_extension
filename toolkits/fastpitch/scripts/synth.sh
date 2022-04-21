#!/bin/bash

# =====================================================================
# Dealing with configuration
# =====================================================================
# Global
: ${NB_PROCS:=16}

# Fast Pitch
: ${EPOCH:=1500}
: ${EXP:=bc_2013}
: ${PH_DICT:=None}
: ${IMPOSE_DUR:=None}

# WaveNET
: ${WAVENET_EXP_DIR:=$HOME/work/neural_vocoders/wavenet/egs/mol_wg/}
: ${WAVENET_EXP_ID:=bc_2013_orig}
: ${BS:=32}

# WaveGAN
: ${WAVEGAN_EXP_DIR:=$HOME/work/neural_vocoders/ParallelWaveGAN/egs/bc_2013/voc1/}
: ${WG_STEPS:=1500000}

TEST_FILE=$1

# Current Experiment
EXP=$(realpath $EXP) # NOTE: need actual absolute path for wavegan
export DATASET_DIR=$EXP/dataset
export MODELS_DIR=$EXP/models
export MEL_DIR=$EXP/mel
export WAVENET_OUTPUT_DIR=$EXP/wavenet
export WAVEGAN_OUTPUT_DIR=$EXP/wavegan

# =====================================================================
# Generate Mel Spectrograms
# =====================================================================

mkdir -p $MEL_DIR

[ "$PH_DICT" != "None" ] && SYMBOL_OPT="--symbol-dict $PH_DICT"
[ "$IMPOSE_DUR" != "None" ] && IMPOSE_DUR_FLAG="--load-dur"

python inference.py --cuda \
	--fastpitch $MODELS_DIR/FastPitch_checkpoint_${EPOCH}.pt \
	--sampling-rate 16000 --waveglow SKIP \
	$IMPOSE_DUR_FLAG \
	$SYMBOL_OPT \
	-i $TEST_FILE -o $MEL_DIR

# # =====================================================================
# # Rendering using WaveNET
# # =====================================================================
# # Convert FP spectrogram to wavenet
# mkdir -p $WAVENET_OUTPUT_DIR
# tail -n +2 $TEST_FILE |
# 	cut -d$'\t' -f1 |
# 	xargs -P $NB_PROCS -n 1 -I {} python scripts/fastpitch2voc.py -v --voc wn $MEL_DIR/{}.mel $WAVENET_OUTPUT_DIR/{}-feats.npy

# # Rendering
# python ~/work/neural_vocoders/wavenet/evaluate.py \
# 	$WAVENET_OUTPUT_DIR \
# 	$WAVENET_EXP_DIR/exp/${WAVENET_EXP_ID}_train_no_dev_mol_wavenet/checkpoint_latest.pth \
# 	$WAVENET_OUTPUT_DIR \
# 	--preset $WAVENET_EXP_DIR/exp/${WAVENET_EXP_ID}_train_no_dev_mol_wavenet/hparams.json \
# 	--hparams="batch_size=${BS}"

# =====================================================================
# Rendering using WaveGAN
# =====================================================================

# Convert FP spectrogram to wavegan
mkdir -p $WAVEGAN_OUTPUT_DIR
tail -n +2 $TEST_FILE |
	cut -d$'\t' -f1 |
	xargs -P $NB_PROCS -n 1 -I {} python scripts/fastpitch2voc.py -v --voc wg $MEL_DIR/{}.mel $WAVEGAN_OUTPUT_DIR/{}.h5

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
