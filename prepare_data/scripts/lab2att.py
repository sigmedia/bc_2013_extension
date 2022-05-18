#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <sebastien.lemaguer@adaptcentre.ie>

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
import numpy as np

###############################################################################
# global constants
###############################################################################
LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]
HTK_UNIT_MS = 10000
NB_STATES = 5

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
    parser = argparse.ArgumentParser(
        description="Helper to get data FastPitch compatible from Merlin formatted data"
    )

    # Add options
    parser.add_argument(
        "-f",
        "--frameshift_fastpitch",
        type=float,
        default=16,
        help="Frameshift (in ms) of fastpitch",
    )
    parser.add_argument(
        "-F",
        "--frameshift_merlin",
        type=float,
        default=5,
        help="Frameshift (in ms) of merlin",
    )
    parser.add_argument("-l", "--log_file", default=None, help="Logger file")
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )

    # Add arguments
    parser.add_argument("merlin_lab_file", help="The label file generated for merlin")
    parser.add_argument(
        "attention_file",
        help="The duration file to generate for fastpitch (output)",
    )

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

    dur_vector = np.round(np.array(durations) / args.frameshift_fastpitch)

    # Generate attension matrix from duration vectory
    nb_frames = int(dur_vector.sum())
    att_matrix = np.zeros((nb_frames, dur_vector.shape[0]))
    cum_i = 0
    for i_ph, cur_dur in enumerate(dur_vector):
        for _ in range(int(cur_dur)):
            att_matrix[cum_i][i_ph] = 1
            cum_i += 1

    np.save(args.attention_file,att_matrix)
