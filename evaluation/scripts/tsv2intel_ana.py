#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <lemagues@tcd.ie>

DESCRIPTION

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 18 May 2022
"""

# Arguments
import argparse

# Messaging/logging
import logging
from logging.config import dictConfig

# Data
import pandas as pd

###############################################################################
# global constants
###############################################################################
LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]

###############################################################################
# Functions
###############################################################################
def configure_logger(args) -> logging.Logger:
    """Setup the global logging configurations and instanciate a specific logger for the current script

    Parameters
    ----------
    args : dict
        The arguments given to the script

    Returns
    --------
    the logger: logger.Logger
    """
    # create logger and formatter
    logger = logging.getLogger()

    # Verbose level => logging level
    log_level = args.verbosity
    if args.verbosity >= len(LEVEL):
        log_level = len(LEVEL) - 1
        # logging.warning("verbosity level is too high, I'm gonna assume you're taking the highest (%d)" % log_level)

    # Define the default logger configuration
    logging_config = dict(
        version=1,
        disable_existing_logger=True,
        formatters={
            "f": {
                "format": "[%(asctime)s] [%(levelname)s] — [%(name)s — %(funcName)s:%(lineno)d] %(message)s",
                "datefmt": "%d/%b/%Y: %H:%M:%S ",
            }
        },
        handlers={
            "h": {
                "class": "logging.StreamHandler",
                "formatter": "f",
                "level": LEVEL[log_level],
            }
        },
        root={"handlers": ["h"], "level": LEVEL[log_level]},
    )

    # Add file handler if file logging required
    if args.log_file is not None:
        logging_config["handlers"]["f"] = {
            "class": "logging.FileHandler",
            "formatter": "f",
            "level": LEVEL[log_level],
            "filename": args.log_file,
        }
        logging_config["root"]["handlers"] = ["h", "f"]

    # Setup logging configuration
    dictConfig(logging_config)

    # Retrieve and return the logger dedicated to the script
    logger = logging.getLogger(__name__)
    return logger


def define_argument_parser() -> argparse.ArgumentParser:
    """Defines the argument parser

    Returns
    --------
    The argument parser: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description="")

    # Add options
    parser.add_argument("-l", "--log_file", default=None, help="Logger file")
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )

    # Add arguments
    parser.add_argument("input_tsv")
    parser.add_argument("output_dir")
    # TODO

    # Return parser
    return parser


###############################################################################
#  Envelopping
###############################################################################
if __name__ == "__main__":
    # Initialization
    arg_parser = define_argument_parser()
    args = arg_parser.parse_args()
    logger = configure_logger(args)

    # Load dataframe
    df = pd.read_csv(args.input_tsv, sep="\t")

    # Extract "correct_sus" file - TODO: add section?
    text_val = list(df["text"].unique())
    dict_val = dict()
    rev_dict_val = dict()
    for i, text in enumerate(text_val):
        dict_val[f"{i:02d}"] = text
        rev_dict_val[text] = f"{i:02d}"
        logger.debug(f"{i:02d} {text}")
    key_result = list(dict_val.keys())
    key_result.sort()
    with open(args.output_dir + "/correct_sus", "w") as f_out:
        for k in key_result:
            f_out.write(f"{k}\t{dict_val[k]}\n")

    # Filter unused informations
    df['id_result_utt'] = df['text'].map(rev_dict_val)
    df_of_interest = df[["user_id", "id_result_utt", "system", "text", "score"]].sort_values(by=["user_id", "id_result_utt"])
    logger.debug("=== Check ordering")
    logger.debug("\n" + str(df_of_interest.head()))

    # Parse
    prev_user = None
    result_list = list()
    cur_user = dict()
    i_key_result = 0
    for row in df_of_interest.iterrows():
        cur_row = row[1] # NOTE: check if we can avoid this
        if cur_row["user_id"] != prev_user:
            if prev_user != None:
                result_list.append(cur_user)

            # Move to next user
            prev_user = cur_row["user_id"]
            i_key_result = 0
            cur_user = {"email": prev_user, "type": "X", "grp": "X", "completed": "X"}

        cur_user[f"result_{key_result[i_key_result]}"] = cur_row["score"]
        i_key_result += 1

    if prev_user != None:
        result_list.append(cur_user)

    # Generate the dataframe needed by HResult.pl
    export_df = pd.DataFrame(result_list)
    logger.debug("=== Check final dataframe")
    logger.debug("\n" + str(export_df.head()))

    export_df.to_csv(args.output_dir + "/results_sus.psv", sep="|", index=False)

    # Generate the system/utt mapping by users
    prev_user = None
    result_list = list()
    cur_user = dict()
    i_key_result = 0
    for row in df_of_interest.iterrows():
        cur_row = row[1] # NOTE: check if we can avoid this
        if cur_row["user_id"] != prev_user:
            if prev_user != None:
                result_list.append(cur_user)

            # Move to next user
            prev_user = cur_row["user_id"]
            i_key_result = 0
            cur_user = {"email": prev_user,}

        cur_user[f"result_{key_result[i_key_result]}"] = cur_row["system"]
        i_key_result += 1

    if prev_user != None:
        result_list.append(cur_user)

    # Generate the dataframe needed by HResult.pl
    export_df = pd.DataFrame(result_list)
    logger.debug("=== Check Result/System mapping")
    logger.debug("\n" + str(export_df.head()))

    export_df.to_csv(args.output_dir + "/map_user_utt_id_system.tsv", sep="\t", index=False)
