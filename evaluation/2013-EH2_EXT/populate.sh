#!/bin/bash

# # Retrieve the information
# (
#     cd ./systems/files/
#     bash -xe retrieve.sh
# )

# Add the reference samples
REF_SAMPLES=(booksent_2013_0057.wav booksent_2013_0077.wav booksent_2013_0043.wav booksent_2013_0088.wav)
for sample in ${REF_SAMPLES[@]}; do
    cp -v ./systems/files/natural16/$sample assets/ref_samples/
done
