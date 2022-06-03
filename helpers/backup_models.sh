#!/bin/bash

# Backup acoustic models
mkdir -p models/fastpitch
cp -rfv toolkits/fastpitch/bc_2013/models/FastPitch_checkpoint_1500.pt models/fastpitch

mkdir -p models/tacotron
cp -rfv toolkits/tacotron/checkpoints/bc_2013_lsa_smooth_attention.tacotron/latest_*.pyt models/tacotron

# Backup neural vocoders
mkdir -p models/parallel_wavegan
cp -rfv toolkits/parallel_wavegan/egs/bc_2013/voc1/exp/train_parallel_wavegan.v1/checkpoint-1500000steps.pkl models/parallel_wavegan
cp -rfv toolkits/parallel_wavegan/egs/bc_2013/voc1/exp/train_parallel_wavegan.v1/config.yml models/parallel_wavegan
cp -rfv toolkits/parallel_wavegan/egs/bc_2013/voc1/exp/train_parallel_wavegan.v1/stats.h5 models/parallel_wavegan

mkdir -p models/wavenet
cp -rfv toolkits/wavenet/egs/bc_2013/exp/bc_2013_train_mol_wavenet/models/checkpoint_latest*.pth models/wavenet
cp -rfv toolkits/wavenet/egs/bc_2013/exp/bc_2013_train_mol_wavenet/models/hparams.json models/wavenet
