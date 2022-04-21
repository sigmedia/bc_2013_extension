#!/bin/bash

export OMP_NUM_THREADS=1

: ${NUM_GPUS:=8}
: ${BS:=32}
: ${GRAD_ACCUMULATION:=1}
: ${AMP:=false}
: ${EPOCHS:=1500}
: ${EXP:=bc_2013}
: ${PH_DICT:=None}
: ${INPUT_DIM:=80}

DATA_DIR=$EXP/dataset
MODEL_DIR=$EXP/models

[ "$AMP" == "true" ] && AMP_FLAG="--amp"
[ "$PH_DICT" != "None" ] && SYMBOL_OPT="--symbol-dict $PH_DICT" 

# Adjust env variables to maintain the global batch size
#
#    NGPU x BS x GRAD_ACC = 256.
#
GBS=$(($NUM_GPUS * $BS * $GRAD_ACCUMULATION))
[ $GBS -ne 256 ] && echo -e "\nWARNING: Global batch size changed from 256 to ${GBS}.\n"

echo -e "\nSetup: ${NUM_GPUS}x${BS}x${GRAD_ACCUMULATION} - global batch size ${GBS}\n"

python -m torch.distributed.launch --nproc_per_node ${NUM_GPUS} train.py \
    --cuda \
    -o "$MODEL_DIR/" \
    --log-file "$MODEL_DIR/nvlog.json" \
    --dataset-path $DATA_DIR \
    --training-files ${DATA_DIR}/filelists/bc_2013_mel_dur_pitch_text_train_filelist.txt \
    --validation-files ${DATA_DIR}/filelists/bc_2013_mel_dur_pitch_text_val_filelist.txt \
    --pitch-mean-std-file ${DATA_DIR}/pitch_char_stats__bc_2013_audio_text_train_filelist.json \
    --resume \
    --epochs ${EPOCHS} \
    --epochs-per-checkpoint 100 \
    --warmup-steps 1000 \
    -lr 0.1 \
    -bs ${BS} \
    --optimizer lamb \
    --grad-clip-thresh 1000.0 \
    --dur-predictor-loss-scale 0.1 \
    --pitch-predictor-loss-scale 0.1 \
    --weight-decay 1e-6 \
    --n-mel-channels $INPUT_DIM \
    --gradient-accumulation-steps ${GRAD_ACCUMULATION} \
    ${AMP_FLAG} \
    ${SYMBOL_OPT}
    
