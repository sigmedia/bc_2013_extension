#!/bin/bash

script_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
VOC_DIR=$script_dir/../../

# Directory that contains all wav files
# **CHANGE** this to your database path
spk="bc_2013"
dumpdir=dump

# train/dev/eval split
dev_size=10
eval_size=10
# Maximum size of train/dev/eval data (in hours).
# set small value (e.g. 0.2) for testing
limit=1000000

# waveform global gain normalization scale
global_gain_scale=0.55

stage=2
stop_stage=3

# Hyper parameters (.json)
# **CHANGE** here to your own hparams
hparams=conf/mol_wavenet.json

# Batch size at inference time.
inference_batch_size=32
# Leave empty to use latest checkpoint
eval_checkpoint=
# Max number of utts. for evaluation( for debugging)
eval_max_num_utt=1000000

# exp tag
tag="" # tag for managing experiments.

. $VOC_DIR/utils/parse_options.sh || exit 1;

# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail

train_set="train"
dev_set="val"
eval_set="test"
datasets=($train_set $dev_set $eval_set)

# exp name
if [ -z ${tag} ]; then
    expname=${spk}_${train_set}_$(basename ${hparams%.*})
else
    expname=${spk}_${train_set}_${tag}
fi
expdir=exp/$expname

# Output directories
dump_norm_dir=$dumpdir/norm # extracted features (pair of <wave, feats>)

if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    echo "stage 2: WaveNet training"
    python $VOC_DIR/train.py \
        --dump-root $dump_norm_dir \
        --preset $hparams \
        --checkpoint-dir=$expdir/models \
        --log-event-path=tensorboard/${expname}
fi

if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    echo "stage 3: Synthesis waveform from WaveNet"
    if [ -z $eval_checkpoint ]; then
      eval_checkpoint=$expdir/models/checkpoint_latest.pth
    fi
    name=$(basename $eval_checkpoint)
    name=${name/.pth/}
    for s in $dev_set $eval_set;
    do
      dst_dir=$expdir/generated/$name/$s
      python $VOC_DIR/evaluate.py $dump_norm_dir/$s $eval_checkpoint $dst_dir \
        --preset $hparams --hparams="batch_size=$inference_batch_size" \
        --num-utterances=$eval_max_num_utt
    done
fi
