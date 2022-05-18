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

# IO
from utils.io import save_wavegan, save_wavenet, save_waveglow, save_wavernn, save_fastpitch
from utils.io import load_wavegan, load_wavenet, load_waveglow, load_wavernn, load_fastpitch

# Data
import numpy as np
import torch

# Audio/signal processing
from scipy import signal
import librosa

###############################################################################
# global constants
###############################################################################

LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]
SUPPORTED_PARAMETRIZATION = set(["wg", "wG", "wn", "wr", "fastpitch", "tacotron"])


###############################################################################
# Neural vocoder helpers & entry function
###############################################################################


def convert(
        input_file: str, output_directory: str, input_type: str, output_type: str
):

    global logger

    # Load it
    if input_type == "wg":
        data = load_wavegan(input_file, "feats")
    elif input_type == "wG":
        data = load_waveglow(input_file)
    elif input_type == "wn":
        data = load_wavenet(input_file)
    elif input_type == "wr":
        data = load_wavernn(input_file)
    elif input_type == "fastpitch":
        data = load_fastpitch(input_file)
    elif input_type == "tacotron":
        data = load_wavenet(input_file)


    # Save it
    if output_type == "wg":
        logger.debug(f"Convert the spectrogram from {Path(input_file).stem} to be compatible with Parallel WaveGAN")
        output_filename = os.path.join(output_directory, Path(input_file).stem + ".h5")
        save_wavegan(data, output_filename)

    elif output_type == "wG":
        logger.debug(f"Convert the spectrogram from {Path(input_file).stem} to be compatible with WaveGlow")
        output_filename = os.path.join(output_directory, Path(input_file).stem + ".pt")
        save_waveglow(data, output_filename)

    elif output_type == "wn":
        logger.debug(f"Convert the spectrogram from {Path(input_file).stem} to be compatible with WaveNet")
        output_filename = os.path.join(
            output_directory, Path(input_file).stem + "-feats.npy"
        )
        save_wavenet(data, output_filename)

    elif output_type == "wr":
        logger.debug(f"Convert the spectrogram from {Path(input_file).stem} to be compatible with WaveRNN")
        output_filename = os.path.join(output_directory, Path(input_file).stem + ".npy")
        save_wavernn(data, output_filename)

    elif output_type == "fastpitch":
        logger.debug(f"Convert the spectrogram from {Path(input_file).stem} to be compatible with FastPitch")
        output_filename = os.path.join(output_directory, Path(input_file).stem + ".pt")
        save_fastpitch(data, output_filename)

    elif output_type == "tacotron":
        logger.debug(f"Convert the spectrogram from {Path(input_file).stem} to be compatible with Tacotron")
        output_filename = os.path.join(output_directory, Path(input_file).stem + ".npy")
        save_wavenet(data, output_filename)


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
        description="Blizzard challenge extension - format conversion script."
    )

    # Add options
    parser.add_argument("-l", "--log_file", default=None, help="Logger file")
    parser.add_argument(
        "-i",
        "--input_parametrization_type",
        default="wg",
        help="The input type of parametrization [wn (wavenet)*, wg (wavegan), wG (waveglow), wr (wavernn)]",
    )
    parser.add_argument(
        "-o",
        "--output_parametrization_type",
        default="wg",
        help="The output type of parametrization [wn (wavenet)*, wg (wavegan), wG (waveglow), wr (wavernn)]",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )

    # Add arguments
    parser.add_argument(
        "input_dir",
        help="the input directory containing the spectrogram files to be converted (directory tree not supported)",
    )
    parser.add_argument("output_directory", help="the output directory")

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
    assert args.input_parametrization_type in SUPPORTED_PARAMETRIZATION, \
        f"{args.input_parametrization_type} is not one of the available supported parametrization: {SUPPORTED_PARAMETRIZATION}"
    assert args.output_parametrization_type in SUPPORTED_PARAMETRIZATION,  \
        f"{args.output_parametrization_type} is not one of the available supported parametrization: {SUPPORTED_PARAMETRIZATION}"

    # Create the directory if needed
    if not Path(args.output_directory).exists():
        os.makedirs(args.output_directory, exist_ok=True)

    # Acoustic parametrization
    for input_file in os.listdir(args.input_dir):
        if input_file.endswith(".h5") or input_file.endswith(".npy") or input_file.endswith(".pt"):
            input_filename = os.path.join(args.input_dir, input_file)
            logger.info(f"Parametrization of {input_filename}")
            convert(input_filename,
                    args.output_directory,
                    args.input_parametrization_type,
                    args.output_parametrization_type)
        else:
            logger.debug(f"{input_file} is not a valid data file (hdf5, numpy, pytorch), it is ignored")
