#!/bin/bash

# Define what to run and on what
: ${TEST_FILE:=$PWD/prepare_data/output/synthesis/prompt_to_synth.tsv}
: ${EXPES:="fp wg wn tac"}

# Define model paths (can be modified)
: ${MODEL_DL_DIR:=$PWD/models}
: ${FP_MODEL:=$MODEL_DL_DIR/fastpitch/FastPitch_checkpoint_1500.pt}
: ${TAC_MODEL:=$MODEL_DL_DIR/tacotron/latest_weights.pyt}
: ${WN_MODEL_DIR:=$MODEL_DL_DIR/wavenet}
: ${WG_MODEL:=$MODEL_DL_DIR/parallel_wavegan/checkpoint-1500000steps.pkl}

# Output directories
: ${OUTPUT_ROOT_DIR:=$PWD/output}
FP_OUTPUT_DIR=$OUTPUT_ROOT_DIR/fastpitch
TAC_OUTPUT_DIR=$OUTPUT_ROOT_DIR/tacotron
WN_OUTPUT_DIR=$OUTPUT_ROOT_DIR/wavenet
WG_OUTPUT_DIR=$OUTPUT_ROOT_DIR/wavegan

# Helper input files
: ${PH_DICT:=$PWD/src/ph_list}
: ${BS:=32}

# Define Toolkit/Experiment paths
FP_TOOLKIT_DIR=$PWD/toolkits/fastpitch
TAC_TOOLKIT_DIR=$PWD/toolkits/tacotron
WN_TOOLKIT_DIR=$PWD/toolkits/wavenet
WN_EXP_DIR=$WN_TOOLKIT_DIR/egs/bc_2013
WG_EXP_DIR=$PWD/toolkits/parallel_wavegan/egs/bc_2013/voc1

EXPES=($(echo $EXPES | tr " " "\n"))


###################
### FastPitch
#############################################################################
if [[ " ${EXPES[*]} " == *" fp "* ]]; then
    mkdir -p $FP_OUTPUT_DIR/orig
    (
        cd $FP_TOOLKIT_DIR;
        python inference.py --cuda \
	         --fastpitch $FP_MODEL \
	         --sampling-rate 16000 --waveglow SKIP \
             --symbol-dict $PH_DICT \
	         -i $TEST_FILE \
             -o $FP_OUTPUT_DIR/orig
    )

    if [[ " ${EXPES[*]} " == *" wg "* ]]; then
        mkdir -p "$FP_OUTPUT_DIR/wg"
        # cp -rfv "$PWD/test_files/${BASENAME}.h5" "$FP_OUTPUT_DIR/wg"

        # Rendering
        (
	        cd $WG_EXP_DIR
	        . ./cmd.sh || exit 1
	        . ./path.sh || exit 1

	        ${cuda_cmd} --gpu "1" /dev/stdout \
		                parallel-wavegan-decode \
		                --dumpdir "$FP_OUTPUT_DIR/wg" \
		                --checkpoint $WG_MODEL \
		                --outdir "$FP_OUTPUT_DIR/wg" \
		                --verbose "1" | tee "$FP_OUTPUT_DIR/wg/decode.log"
        )
    fi


    if [[ " ${EXPES[*]} " == *" wn "* ]]; then
        mkdir -p "$WN_OUTPUT_DIR"
        cp -rfv "$PWD/test_files/${BASENAME}-feats.npy" "$WN_OUTPUT_DIR"

        # Rendering
        python $WN_TOOLKIT_DIR/evaluate.py \
	         $FP_OUTPUT_DIR/wn \
	         $WN_MODEL_DIR/checkpoint_latest.pth \
	         $FP_OUTPUT_DIR/wn \
	         --preset $WN_MODEL_DIR/hparams.json \
	         --hparams="batch_size=${BS}"
    fi
fi

exit 0

###################
### Tacotron
#############################################################################
if [[ " ${EXPES[*]} " == *" tac "* ]]; then
    mkdir -p $TAC_OUTPUT_DIR/orig
    (
        cd $TAC_TOOLKIT_DIR;
        echo python gen_tacotron.py \
             --symbol-dict $PH_DICT \
             --hp_file hparams.py \
             --tts_weights $TAC_MODEL \
             --save_attention \
             -O $TAC_OUTPUT_DIR/orig \
             -I $TEST_FILE \
             none
    )
fi

exit 0
