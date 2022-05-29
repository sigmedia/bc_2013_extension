#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <lemagues@tcd.ie>

DESCRIPTION

    Helper to anonymize the result dataframe extracted from the FlexEval database

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 16 May 2022
"""

# Arguments
import argparse

# Data
import pandas as pd

# Dealing with argument
arg_parser = define_argument_parser()
arg_parser = argparse.ArgumentParser(description="")
arg_parser.add_argument("input_df_file", help="Dataframe to anonymize (TSV format)")
arg_parser.add_argument("output_df_file", help="Anonymized output file (TSV format )")
args = arg_parser.parse_args()

# Load the dataframe file
cur_df = pd.read_csv(args.input_df_file, sep="\t")

# Generate a dict to associate a user_id to its index (index will be new user_id)
user_ids = dict()
for i_user, cur_id in enumerate(cur_df["user_id"].unique()):
    user_ids[cur_id] = i_user

# Anonymize and save the anonymized dataframe
cur_df.replace(user_ids, inplace=True)
cur_df.to_csv(args.output_df_file, sep="\t",index=False)
