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
        "--frameshift",
        type=float,
        default=16,
        help="Frameshift (in ms)",
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
    parser.add_argument("mel_file", help="The mel spectrogram file")
    parser.add_argument(
        "attention_file",
        help="The duration file to generate for fastpitch (output)",
    )

    # Return parser
    return parser


def dur2guide(dur: np.ndarray, mel_nb_frames: int) -> np.ndarray:
    """Generate the attention guide give the duration array and the maximal number of frames

    Parameters
    ----------
    dur: ndarray (nb_phones,)
        The array of phone durations
    mel_nb_frames: unsigned int
        The number of frames of the mel spectrogram

    Returns
    -------
    np.ndarray (nb_phones, mel_nb_frames)
        the array of duration per phone
    """
    att_guide = np.zeros((dur.shape[0], mel_nb_frames))
    cur_i = 0
    for d_i, d in enumerate(dur):
        for i in range(int(d.item())):
            att_guide[d_i, cur_i] = 1
            cur_i += 1

    for i in range(cur_i, mel_nb_frames):
        att_guide[-1, i] = 1

    return att_guide.T


def lab2dur(label_file_name: str, frameshift: int) -> np.ndarray:
    """Load the duration from a given label file

    Parameters
    ----------
    label_file_name: str
       The path to the label file
    frameshift: int
       The frameshift in ms

    Returns
    -------
    np.ndarray (nb_phones,)
        the array of duration per phone
    """

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

    return np.round(np.array(durations) / frameshift)


###############################################################################
#  Envelopping
###############################################################################
if __name__ == "__main__":
    # Initialization
    arg_parser = define_argument_parser()
    args = arg_parser.parse_args()
    logger = configure_logger(args)

    # Load the duration
    dur = lab2dur(args.merlin_lab_file, args.frameshift)

    # Ensure compatibility between the duration and number of frames
    mel_nb_frames = np.load(args.mel_file).shape[1]

    if mel_nb_frames < int(dur.sum().item()):
        logger.warning(
            f'The file "{args.mel_file}" contains {mel_nb_frames} which is less than the expected durations {int(dur.sum().item())}, trying to patch'
        )

        # We authorize a fix only in the two last segments (the last one being a silence!)
        # FIXME: this is really patchy!
        diff = mel_nb_frames - int(dur.sum().item())
        if np.abs(diff) < (dur[-1] + dur[-2]).item():
            dur[-1] += diff
            if dur[-1] <= 0:
                dur[-2] += dur[-1] - 1
                dur[-1] = 1
        else:
            logger.error(
                f'I don\'t know how to deal with the file "{args.mel_file}": mel_nb_frames={mel_nb_frames}, diff_with_dur={diff}, last_phones_durations={dur[-4:]}; move to the next file'
            )
            sys.exit(-1)
    else:
        logger.debug(
            f'The file "{args.mel_file}" contains {mel_nb_frames} and the expected total duration is {int(dur.sum().item())}'
        )

    # Generate attention guideline and save it
    att = dur2guide(dur, mel_nb_frames)
    np.save(args.attention_file, att)
