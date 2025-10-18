#!/bin/bash

# Retrieve the information
(
    cd ./systems/files/
    bash -xe retrieve.sh
)

# Apply degradation script
mkdir -p systems/files/degraded
PHASE_ARRAY=("core_test" "intro")
for PHASE in ${PHASE_ARRAY[@]}; do
    cat systems/$PHASE/degraded.tsv | cut -d$'\t' -f1 | tail -n +2 | sed 's%\(.*\)/degraded/\(.*\)%python helpers/degrade.py systems/\1/natural16/\2 systems/\1/degraded/\2%g' | xargs -I {} bash -xec '{}'
done
