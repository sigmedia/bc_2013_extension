#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <lemagues@tcd.ie>

# Copyright 2019 Tomoki Hayashi
#  MIT License (https://opensource.org/licenses/MIT)
DESCRIPTION

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 14 May 2022
"""

import sys

# Arguments
import argparse

# Messaging/logging
import logging
from logging.config import dictConfig
from tqdm import tqdm

# IO
import os
import pathlib
from utils.io import read_hdf5, save_wavegan

# Data
import numpy as np
from sklearn.preprocessing import StandardScaler

###############################################################################
# global constants
###############################################################################
LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]

###############################################################################
# IO Utils
###############################################################################


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
    parser.add_argument("-L", "--list_files", default=None, help="List of files to normalize")
    parser.add_argument("-l", "--log_file", default=None, help="Logger file")
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )

    # Add arguments
    parser.add_argument("scaler", help="The scaler to use for the normalization")
    parser.add_argument("input_dir", help="The directory containing the input files to normalize")
    parser.add_argument("output_dir", help="The output directory")

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

    # List files
    # NOTE: only using wavegan format for now, convert scripts available
    in_dir = pathlib.Path(args.input_dir)
    out_dir = pathlib.Path(args.output_dir)
    if args.list_files is None:
        list_files = list(in_dir.glob('**/*.h5'))
    else:
        list_files = []
        with open(args.list_files) as f:
            for cur_base in f:
                cur_base = cur_base.strip()
                list_files.append(in_dir/(cur_base + ".h5"))


    # restore scaler (NOTE: only WaveGAN supported for now)
    scaler = StandardScaler()
    if args.scaler.endswith(".h5"):
        scaler.mean_ = read_hdf5(args.scaler, "mean")
        scaler.scale_ = read_hdf5(args.scaler, "scale")
    elif args.scaler.endswith(".npy"):
        scaler.mean_ = np.load(args.stats)[0]
        scaler.scale_ = np.load(args.stats)[1]
    else:
        raise ValueError("support only hdf5 or npy format.")

    scaler.n_features_in_ = scaler.mean_.shape[0] # from version 0.23.0, this information is needed

    # Normalize
    for mel_fn in tqdm(list_files):
        mel = read_hdf5(mel_fn, "feats")
        mel = scaler.transform(mel)
        rel_path = mel_fn.relative_to(in_dir)
        out_path = out_dir/rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        save_wavegan(mel, out_path)
