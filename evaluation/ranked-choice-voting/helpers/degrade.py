#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <sebastien.lemaguer@helsinki.fi>

DESCRIPTION
    This script provides a way to generate highly degraded samples for a subjective evaluation

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 16 October 2025
"""


# Core Python
import argparse
import pathlib

# Numerical
import scipy.signal as sig
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import numpy as np


# Messaging/logging
import logging
from logging.config import dictConfig
try:
    import pythonjsonlogger
    JSON_LOGGER = True
except Exception:
    JSON_LOGGER = False

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
        cur_formatter_key = "f"
        if JSON_LOGGER:
            logging_config["formatters"]["j"] = {
                '()': 'pythonjsonlogger.json.JsonFormatter',
                'fmt': '%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s',
                'rename_fields': {'asctime': 'time', 'levelname': 'level', 'lineno': 'line_number'}
            }
            cur_formatter_key = "j"

        logging_config["handlers"]["f"] = {
            "class": "logging.FileHandler",
            "formatter": cur_formatter_key,
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

    # Add logging options
    parser.add_argument("-l", "--log_file", default=None, help="Logger file")
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )

    # Add arguments
    parser.add_argument("input_wav", help="The wav file to degrade")
    parser.add_argument("output_wav", help="The degraded wav file")

    # Return parser
    return parser

# Normalisation function
def normalize(audio:np.ndarray) -> np.ndarray:
    return audio / np.max(np.abs(audio))

# Add Gaussian Noise
def add_noise(audio:np.ndarray, noise_factor:float=0.005) -> np.ndarray:
    noise = np.random.randn(len(audio))
    return audio + noise_factor * noise

def low_pass_filter(audio:np.ndarray, cutoff:int=1000, fs:int=16000, order:int=5) -> np.ndarray:
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, audio)

def add_reverb(audio:np.ndarray, decay:float=0.5) -> np.ndarray:
    reverb_filter = np.zeros(500)
    reverb_filter[0] = 1
    reverb_filter[int(500 * decay)] = decay
    return sig.fftconvolve(audio, reverb_filter)[:len(audio)]

def fade_out(audio: np.ndarray, sample_rate:int, duration:float=0.5) -> np.ndarray:
    fade_samples = int(sample_rate * duration)
    fade_curve = np.linspace(1.0, 0.0, fade_samples)
    audio[-fade_samples:] *= fade_curve
    return audio

def degrade(input_wav: pathlib.Path, output_wav: pathlib.Path):

    # Load wav file
    sample_rate, audio = wavfile.read(input_wav)

    # set everything at 2s
    audio = audio[:int(sample_rate*2)]

    # Degrade the signal
    audio = normalize(low_pass_filter(audio,400))
    audio = normalize(add_noise(audio, 0.005))
    audio = normalize(add_reverb(audio))
    audio = fade_out(audio, sample_rate, 0.5)

    # Save wav file in 16-bit signed integer PCM
    audio = (audio * 32767).astype(np.int16)
    wavfile.write(output_wav, sample_rate, audio)


###############################################################################
# Entry point
###############################################################################
def main():
    # Initialization of the argument parser and the logger
    arg_parser = define_argument_parser()
    args = arg_parser.parse_args()
    logger = configure_logger(args)

    degrade(pathlib.Path(args.input_wav), pathlib.Path(args.output_wav))

###############################################################################
# Wrapping for directly calling the scripts
###############################################################################
if __name__ == "__main__":
    main()
