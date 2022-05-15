#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <lemagues@tcd.ie>

DESCRIPTION

# Copyright 2019 Tomoki Hayashi
#  MIT License (https://opensource.org/licenses/MIT)

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 25 August 2021
"""

# Python
import os
from pathlib import Path
from typing import List

# Arguments
import argparse

# Messaging/logging
import logging
from logging.config import dictConfig

# Audio/signal processing
import librosa
import pyworld as pw
import numpy as np

###############################################################################
# global constants
###############################################################################

LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]

###############################################################################
# Wrapping Functions
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
        description="Blizzard challenge extension - parametrization script."
    )

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
    parser.add_argument(
        "wav_file",
        help="the input wav file",
    )
    parser.add_argument("f0_file", help="the output f0 file")

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

    # Load wav
    logger.info(f"Extract F0 from {args.wav_file} to {args.f0_file}")
    x, sr = librosa.load(args.wav_file,sr=None)
    x = x.astype(np.float64)

    # Extract F0
    _f0, t = pw.dio(x, sr)
    f0 = pw.stonemask(x, _f0, t, sr)

    # Save f0
    f0.tofile(args.f0_file)
