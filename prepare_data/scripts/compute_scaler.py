#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <lemagues@tcd.ie>

DESCRIPTION

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 17 May 2022
"""

# Python
import os
import pathlib
import sys

# Beautifier
from tqdm import tqdm

# Arguments
import argparse

# Messaging/logging
import logging
from logging.config import dictConfig

# Data
from sklearn.preprocessing import StandardScaler
import numpy as np

# IO
from utils.io import load_wavegan, load_wavenet, load_waveglow, load_wavernn
from utils.io import write_hdf5

###############################################################################
# global constants
###############################################################################
LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]
SUPPORTED_PARAMETRIZATION = set(["wg", "wG", "wn", "wr"])

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
    parser.add_argument("-L", "--list_files", default=None, help="List of files used to compute the scaler")
    parser.add_argument("-l", "--log_file", default=None, help="Logger file")
    parser.add_argument(
        "-t",
        "--parametrization_type",
        default="wg",
        help="The type of parametrization expected [wn (wavenet)*, wg (wavegan), wG (waveglow), wr (wavernn)]",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )

    # Add arguments
    parser.add_argument("input_dir", help="Directory containing the input files")
    parser.add_argument("output_file", help="Scaler file")
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

    # Validate the types
    assert args.parametrization_type in SUPPORTED_PARAMETRIZATION, \
        f"{args.parametrization_type} is not one of the available supported parametrization: {SUPPORTED_PARAMETRIZATION}"


    # Define extension
    ext = ".npy"
    if args.parametrization_type == "wg": # WaveGAN
        ext = ".h5"
    elif args.parametrization_type == "wG": # WaveGLOW
        ext = ".pt"
    elif args.parametrization_type == "wn": # WaveNet
        ext = "-feats.npy"
    elif args.parametrization_type == "wr": # WaveRNN
        ext = ".npy"

    # List files
    in_dir = pathlib.Path(args.input_dir)
    if args.list_files is None:
        list_files = list(in_dir.glob(f'**/*{ext}'))
    else:
        list_files = []
        with open(args.list_files) as f:
            for cur_base in f:
                cur_base = cur_base.strip()
                list_files.append(in_dir/(cur_base + ext))


    scaler = StandardScaler()
    for input_file in tqdm(list_files):
        # Load the data
        if args.parametrization_type == "wg":
            data = load_wavegan(input_file, "feats")
        elif args.parametrization_type == "wG":
            data = load_waveglow(input_file)
        elif args.parametrization_type == "wn":
            data = load_wavenet(input_file)
        elif args.parametrization_type == "wr":
            data = load_wavernn(input_file)

        # Scale
        scaler.partial_fit(data)


    write_hdf5(
        args.output_file,
        "mean",
        scaler.mean_.astype(np.float32),
    )
    write_hdf5(
        args.output_file,
        "scale",
        scaler.scale_.astype(np.float32),
    )
