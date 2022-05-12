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

# System/default
import sys
import os

# Arguments
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument("-f", "--format", default="tacotron", help="The type of output file required")
parser.add_argument("full_prompt_file", help="The prompt file containg all the utterances")
parser.add_argument("list_utt_file", help="The file containing the sublist of prompts desired")
parser.add_argument("sub_prompt_file", help="The prompt file containing the sublist")
args = parser.parse_args()

# Check format
format = args.format.lower()
if format not in ("tacotron", "fastpitch"):
    raise Exception(f"{format} is not valid, it should be one of these values: tacotron, fastpitch")

# Load the file list to a set
with open(args.list_utt_file) as f:
    set_utts = set([l.strip() for l in f])
# Generate prompt list
list_prompts = []
with open(args.full_prompt_file) as f:
    for l in f:
        elts = l.strip().split("|")
        if elts[0] in set_utts:
            # build pathes (FIXME: hardcoded)
            mel_path = f"mels/{elts[0]}.pt"

            if format == "tacotron":
                list_prompts.append(f"{elts[0]}|{elts[1]}")
            elif format == "fastpitch":
                # build pathes (FIXME: hardcoded)
                dur_path = f"dur/{elts[0]}.pt"
                f0_path  = f"f0/{elts[0]}.pt"
                list_prompts.append(f"{mel_path}|{dur_path}|{f0_path}|{elts[1]}")

# Save the prompts
with open(args.sub_prompt_file, "w") as f_out:
    f_out.write("\n".join(list_prompts))
