#!/usr/bin/bash

# Define input/output variables
MARY_CONFIG=$PWD/configurations/synthesis_config.json
INPUT_TEXT_DIR=$PWD/../src/test/txt
OUTPUT_DIR=$PWD/output/synthesis

# Define temp variables
TMP_DIR=$PWD/tmp/synthesis
TMP_FULL_LAB_DIR=$TMP_DIR/labels/full
TMP_MONO_LAB_DIR=$TMP_DIR/labels/mono

# Prepare directories
mkdir -p $TMP_MONO_LAB_DIR $TMP_FULL_LAB_DIR $OUTPUT_DIR

# Split prompts to text and generate list file
ls -1 $INPUT_TEXT_DIR | sed 's/.txt//g' > $TMP_DIR/list_files

# Generate full labels
(
	cd ../toolkits/marytts/synth_label_generation;
	./gradlew --include-build=../marytts \
                b -Pconf=$MARY_CONFIG \
                -Ptxt_dir=$INPUT_TEXT_DIR \
                -Pfull_lab_dir=$TMP_FULL_LAB_DIR \
                -Pmono_lab_dir=$TMP_MONO_LAB_DIR \
	            -Plist_filename=$TMP_DIR/list_files \
                --stacktrace \
                --max-workers=1 \
                --info

)

# Generate prompt from the labels
#   - NOTE: for whatever reason MaryTTS generate a pau for the quotes
#           it is filtered out
echo -e "output\ttext" > $OUTPUT_DIR/prompt_to_synth.tsv
ls -1 $TMP_MONO_LAB_DIR | \
    xargs -I {} \
          awk -f scripts/generate_synth_prompt.awk $TMP_MONO_LAB_DIR/{} | \
    sed 's/ pau"//g' >> $OUTPUT_DIR/prompt_to_synth.tsv
