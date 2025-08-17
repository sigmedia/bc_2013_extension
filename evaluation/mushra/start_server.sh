#!/bin/bash -xe

flexeval -i 0.0.0.0 -p 4050 -u https://tts-eval-24.it.helsinki.fi/rpt_suomi -P $PWD/structure.yaml -t -vv -l run.log
