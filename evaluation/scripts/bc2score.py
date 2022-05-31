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
    parser.add_argument("full_df_file")
    parser.add_argument("correct_file")
    parser.add_argument("wer_file")
    parser.add_argument("map_sys_res_id_file")
    parser.add_argument("output_df_file")
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

    # Load full df file
    full_df = pd.read_csv(args.full_df_file, sep="\t")

    # The score becomes the transcription now
    # NOTE: maybe dealing with this in the original script? :D
    full_df.rename(columns={"score": "transcription"}, inplace=True)
    full_df["score_type"] = "WER"
    logger.debug("=== Check full df")
    logger.debug("\n" + str(full_df.head()))

    # Load CORRECT file
    correct_df = pd.read_csv(args.correct_file, sep="\t", header=None, names=["utt_id", "text"])
    correct_df["utt_id"] = correct_df["utt_id"].apply(lambda x: f"result_{x:02d}")
    logger.debug("=== Check CORRECT")
    logger.debug("\n" + str(correct_df.head()))

    # Load WER file
    wer_df = pd.read_csv(args.wer_file, sep="|")
    wer_df.drop(["type", "grp", "completed"], axis=1, inplace=True)
    wer_df = wer_df.melt(id_vars=["email"],
                         var_name="utt_id",
                         value_name="score")

    logger.debug("=== Check WER")
    logger.debug("\n" + str(wer_df.head()))

    # Load Mapping file
    map_df = pd.read_csv(args.map_sys_res_id_file, sep="\t")
    map_df = map_df.melt(id_vars=["email"],
                         var_name="utt_id",
                         value_name="system")

    logger.debug("=== Check MAP")
    logger.debug("\n" + str(map_df.head()))

    # Generate intermediate
    wer_df = wer_df.merge(map_df, on=["email", "utt_id"])
    wer_df.rename(columns={"email":"user_id"}, inplace=True)
    logger.debug("=== Check Intermediate")
    logger.debug("\n" + str(wer_df.head()))

    # Join everything now
    full_df = full_df.merge(correct_df, on="text")
    full_df = full_df.merge(wer_df, on=["user_id", "utt_id", "system"])
    logger.debug("=== Check Final")
    logger.debug("\n" + str(full_df.head()))
    full_df.to_csv(args.output_df_file, sep="\t", index=False)
