#!/bin/bash

# Download the archive
wget  -O 2013-EH2-EXT.tar https://data.cstr.ed.ac.uk/blizzard/wavs_and_scores/2013-EH2-EXT.tar.gz

# Untar it (yes the extension is wrong, it's my fault)
tar -xvf 2013-EH2-EXT.tar

# Now copy wav files
SYSTEMS=("C" "CTRL" "fastpitch_wg" "fastpitch_wn" "K" "N" "natural16" "tacotron_wg" "tacotron_wn")
for system in ${SYSTEMS[@]}; do
    mkdir $system
    cp -v 2013-EH2-EXT/$system/submission_directory/2013/EH2-EXT/audiobook_sentences/*.wav $system
    cp -v 2013-EH2-EXT/$system/submission_directory/2013/EH2-EXT/sus/*.wav $system
    cp -v 2013-EH2-EXT/$system/submission_directory/2013/EH2-EXT/news/*.wav $system
done

# Clean unnecessary part
rm -rfv 2013-EH2-EXT*
