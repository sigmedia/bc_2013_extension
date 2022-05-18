#!/bin/bash

VERB_FLAG=""
INPUT_ROOT_DIR=../src/test/eval_results
OUTPUT_ROOT_DIR=./output
TMP_ROOT_DIR=$OUTPUT_ROOT_DIR/tmp

# Prepare environment
mkdir -p $TMP_ROOT_DIR
export PERL5LIB="$PWD/scripts:$PERL5LIB" # Ensure SENTWER.pm is in the PERL5LIB

# Extract files
python scripts/tsv2intel_ana.py $VERB_FLAG $INPUT_ROOT_DIR/intel.tsv $TMP_ROOT_DIR

# Compute WER using blizzard scripts
./scripts/HResults.pl $TMP_ROOT_DIR/correct_sus $TMP_ROOT_DIR/results_sus.psv \
              $TMP_ROOT_DIR/intel_results.psv \
              $INPUT_ROOT_DIR/dictionary # $INPUT_ROOT_DIR/acceptable_variants

# Generate Score file
python scripts/bc2score.py $VERB_FLAG $INPUT_ROOT_DIR/intel.tsv $TMP_ROOT_DIR/correct_sus $TMP_ROOT_DIR/intel_results.psv $TMP_ROOT_DIR/map_user_utt_id_system.tsv $OUTPUT_ROOT_DIR/intel_result.tsv
