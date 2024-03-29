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
import yaml
from utils.io import save_wavegan, save_wavenet, save_waveglow, save_wavernn

# Data
from sklearn.preprocessing import StandardScaler
import numpy as np
import torch

# Audio/signal processing
from scipy import signal
import librosa
from nnmnkwii import preprocessing as P

###############################################################################
# global constants
###############################################################################

LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]
SUPPORTED_PARAMETRIZATION = set(["wg", "wG", "wn", "wr"])

###############################################################################
# IO Utils
###############################################################################

class DictObjectView:
    def __init__(self, in_dict:dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [DictView(x) if isinstance(x, dict) else x for x in val])
            else:
                setattr(self, key, DictView(val) if isinstance(val, dict) else val)

def load_configuration(config_file):
    """Helper to load the configuration file

    Parameters
    ----------
    config_file: string
        The path to the configuration file

    Returns
    -------
    The configuration object

    """
    if args.configuration_file.endswith(".py"):
        import importlib
        config_path = Path(args.configuration_file)
        config = importlib.import_module(
            config_path.stem, os.path.abspath(config_path.parent)
        )

    if args.configuration_file.endswith(".yml") or  args.configuration_file.endswith(".yaml"):
        with open(args.configuration_file) as f:
            config = yaml.load(f, Loader=yaml.Loader)

        config = DictObjectView(config)

    else:
        raise Exception(
            "Configuration type not yet supported, only python modules are taken into accounts"
        )

    return config


###############################################################################
# Extraction
###############################################################################

def get_hop_size(config):
    hop_size = config.hop_size
    if hop_size is None:
        assert config.frame_shift_ms is not None
        hop_size = int(config.frame_shift_ms / 1000 * config.sample_rate)
    return hop_size

def preemphasis(x, coef=0.85):
    return P.preemphasis(x, coef)

def inv_preemphasis(x, coef=0.85):
    return P.inv_preemphasis(x, coef)

def parametrize_wav(x, config):

    # Trim begin/end silences
    # NOTE: the threshold was chosen for clean signals
    # x, _ = librosa.effects.trim(x, top_db=60, frame_length=2048, hop_length=512)

    # if hparams.highpass_cutoff > 0.0:
    #     x = audio.low_cut_filter(x, hparams.sample_rate, hparams.highpass_cutoff)


    # trim silence
    if hasattr(config, "trim_silence") and config.trim_silence:
        x, _ = librosa.effects.trim(
            x,
            top_db=config.trim_threshold_in_db,
            frame_length=config.trim_frame_size,
            hop_length=config.trim_hop_size,
        )

    # Quantization if required
    if config.input_type == "mulaw-quantize":
        # Trim silences in mul-aw quantized domain
        silence_threshold = 0
        if silence_threshold > 0:
            # [0, quantize_channels)
            out = P.mulaw_quantize(x, config.quantize_channels - 1)
            start, end = audio.start_and_end_indices(out, silence_threshold)
            x = x[start:end]
        constant_values = P.mulaw_quantize(0, config.quantize_channels - 1)
        out_dtype = np.int16
    elif config.input_type == "mulaw":
        # [-1, 1]
        constant_values = P.mulaw(0.0, config.quantize_channels - 1)
        out_dtype = np.float32
    elif config.input_type == "raw":
        # [-1, 1]
        constant_values = 0.0
        out_dtype = np.float32
    else:
        raise Exception(f"{config.input_type} is unkwown")

    # Scale the gain (if required)
    if config.global_gain_scale > 0:
        x *= config.global_gain_scale

    # Time domain preprocessing
    if hasattr(config, "preprocess") and \
       config.preprocess is not None and \
       config.preprocess not in ["", "none"]:
        f = globals()[config.preprocess]
        x = f(x)

    # Clip
    if np.abs(x).max() > 1.0:
        logger.warning("""abs max value exceeds 1.0 (val={}); signal will be clipped""".format(np.abs(x).max()))

    x = np.clip(x, -1.0, 1.0)

    # Set xeform target (out)
    if config.input_type == "mulaw-quantize":
        out = P.mulaw_quantize(x, config.quantize_channels - 1)
    elif config.input_type == "mulaw":
        out = P.mulaw(x, config.quantize_channels - 1)
    elif config.input_type == "raw":
        out = x
    else:
        raise Exception(f"{config.input_type} is not a valid input type")

    # zero pad: this is needed to adjust time resolution between audio
    # and mel-spectrogram
    N = (len(x) // get_hop_size(config)) + 1
    if config.pad_mode == "constant":
        out = np.pad(out, (0, config.fft_size), mode=config.pad_mode, constant_values=constant_values)
    else:
        out = np.pad(out, (0, config.fft_size), mode=config.pad_mode)

    assert len(out) >= N * get_hop_size(config)

    # time resolution adjustment: ensure length of raw audio is
    # multiple of hop_size so that we can use transposed convolution
    # to upsample
    out = out[:N * get_hop_size(config)]
    assert len(out) % get_hop_size(config) == 0

    return out

###############################################################################
# Entry Function
###############################################################################

def parametrize_wavfile(
    wav_file: str, output_directory: str, config, parametrization_type: str
):

    global logger

    # Load wav
    x, _ = librosa.load(wav_file, sr=config.sampling_rate)

    # Extract the mel spectrogram
    data = parametrize_wav(x, config)

    # Save it
    # - WaveGAN - TODO: add repo URL
    if parametrization_type == "wg":
        logger.debug(f"Save the parametrized waveform extracted from {Path(wav_file).stem} to be compatible with Parallel WaveGAN")
        output_filename = os.path.join(output_directory, Path(wav_file).stem + ".h5")
        save_wavegan(data, output_filename, "wave")

    # - WaveGlow - TODO: add repo URL
    elif parametrization_type == "wG":
        logger.debug(f"Save the parametrized waveform extracted from {Path(wav_file).stem} to be compatible with WaveGlow")
        output_filename = os.path.join(output_directory, Path(wav_file).stem + ".pt")
        save_waveglow(data, output_filename)

    # - WaveNet - TODO: add repo URL
    elif parametrization_type == "wn":
        logger.debug(f"Save the parametrized waveform extracted from {Path(wav_file).stem} to be compatible with WaveNet")
        output_filename = os.path.join(
            output_directory, Path(wav_file).stem + "-wave.npy"
        )
        save_wavenet(data, output_filename)

    # - WaveRNN - TODO: add repo URL
    elif parametrization_type == "wr":
        logger.debug(f"Save the parametrized waveform extracted from {Path(wav_file).stem} to be compatible with WaveRNN")
        output_filename = os.path.join(output_directory, Path(wav_file).stem + ".npy")
        save_wavernn(data, output_filename)


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
    parser.add_argument(
        "-c",
        "--configuration_file",
        required=True,
        type=str,
        help="The configuration file necessary for the parametrization",
    )
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
    parser.add_argument(
        "input_wav",
        help="the input wav file or directory containing the wav files (directory tree not supported)",
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
    assert args.parametrization_type in SUPPORTED_PARAMETRIZATION, f"{args.parametrization_type} is not one of the available supported parametrization: {SUPPORTED_PARAMETRIZATION}"

    # Load configuration
    config = load_configuration(args.configuration_file)

    # Create the directory if needed
    if not Path(args.output_directory).exists():
        os.makedirs(args.output_directory, exist_ok=True)

    # Acoustic parametrization
    if Path(args.input_wav).is_file():
        logger.info(f"Parametrization of {args.input_wav}")
        parametrize_wavfile(
            args.input_wav, args.output_directory, config, args.parametrization_type
        )
    elif Path(args.input_wav).is_dir():
        for wav_file in os.listdir(args.input_wav):
            if wav_file.endswith(".wav"):
                input_filename = os.path.join(args.input_wav, wav_file)
                logger.info(f"Parametrization of {input_filename}")
                parametrize_wavfile(
                    input_filename,
                    args.output_directory,
                    config,
                    args.parametrization_type,
                )
            else:
                logger.debug(f"{wav_file} is not a wav file, it is ignored")
    else:
        raise Exception(f"{args.input_wav} is neither a file or a directory")
