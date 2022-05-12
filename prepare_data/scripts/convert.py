#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <lemagues@tcd.ie>

DESCRIPTION

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 28 May 2021
"""

# Math
import torch
import numpy as np

# Arguments
import argparse

###############################################################################
# Functions
###############################################################################
HTK_UNIT_MS = 10000
NB_STATES=5

parser = argparse.ArgumentParser(description="")
parser.add_argument("-f", "--frameshift_fastpitch", type=float, default=16, help="Frameshift (in ms) of fastpitch")
parser.add_argument("-F", "--frameshift_merlin", type=float, default=5, help="Frameshift (in ms) of merlin")
parser.add_argument("merlin_lab_file", help="The label file generated for merlin")
parser.add_argument("merlin_f0_file", help="The f0 file extracted for merlin")
parser.add_argument("fastpitch_dur_file", help="The duration file to generate for fastpitch (output)")
parser.add_argument("fastpitch_f0_file", help="The f0 file to generate for fastpitch (output)")
args = parser.parse_args()


# Extract duration from label
durations = []
with open(args.merlin_lab_file) as f:
    lines = [l.strip() for l in f]


# Line ending with "]" => state mode, else phone mode
if lines[0].endswith("]"):
    start = 0
    max_states = NB_STATES + 2 - 1
    for l in lines:
        # check if we are phone mode or in
        if l.endswith(f"{max_states}]"):
            elts = l.split()
            dur = int(elts[1]) // HTK_UNIT_MS - start
            durations.append(dur)

            start = int(elts[1]) // HTK_UNIT_MS
else:
    total_dur = 0
    for l in lines:
        elts = l.split()
        dur = (int(elts[1]) - int(elts[0])) // HTK_UNIT_MS
        total_dur += dur
        durations.append(dur)

dur_tensor = torch.round(torch.Tensor(durations) / args.frameshift_fastpitch)
torch.save(dur_tensor, args.fastpitch_dur_file)

# Compute f0
avg_ph_f0_values = []
# f0 = np.fromfile(args.merlin_f0_file, dtype=np.float32) #FIXME: need to double check wtf!
f0 = np.fromfile(args.merlin_f0_file)
start = 0
for d in durations:
    # Get F0 associated to the segment
    dur_fr = d // args.frameshift_merlin
    sub_f0 = f0[start:start+dur_fr]
    sub_f0 = sub_f0[sub_f0 > 0]

    # Average F0 as segment representative (no voiced -> 0)
    if len(sub_f0) == 0:
        avg_ph_f0_values.append(0)
    else:
        avg_ph_f0_values.append(np.mean(sub_f0))

    # Move to next segment
    start += dur_fr

f0_tensor = torch.Tensor(avg_ph_f0_values)
torch.save(f0_tensor, args.fastpitch_f0_file)
