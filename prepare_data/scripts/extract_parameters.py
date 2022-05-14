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
import h5py
import yaml

# Data
from sklearn.preprocessing import StandardScaler
import numpy as np
import torch

# Audio/signal processing
from scipy import signal
import librosa

###############################################################################
# global constants
###############################################################################

LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]
SUPPORTED_PARAMETRIZATION = set(["wg", "wG", "wn", "wr"])

###############################################################################
# IO Utils
###############################################################################

def read_hdf5(hdf5_name, hdf5_path):
    """Read hdf5 dataset.

    Args:
        hdf5_name (str): Filename of hdf5 file.
        hdf5_path (str): Dataset name in hdf5 file.

    Return:
        any: Dataset values.

    """
    if not os.path.exists(hdf5_name):
        logging.error(f"There is no such a hdf5 file ({hdf5_name}).")
        sys.exit(1)

    hdf5_file = h5py.File(hdf5_name, "r")

    if hdf5_path not in hdf5_file:
        logging.error(f"There is no such a data in hdf5 file. ({hdf5_path})")
        sys.exit(1)

    hdf5_data = hdf5_file[hdf5_path][()]
    hdf5_file.close()

    return hdf5_data

def write_hdf5(hdf5_name, hdf5_path, write_data, is_overwrite=True):
    """Write dataset to hdf5.

    Args:
        hdf5_name (str): Hdf5 dataset filename.
        hdf5_path (str): Dataset path in hdf5.
        write_data (ndarray): Data to write.
        is_overwrite (bool): Whether to overwrite dataset.

    """
    # convert to numpy array
    write_data = np.array(write_data)

    # check folder existence
    folder_name, _ = os.path.split(hdf5_name)
    if not os.path.exists(folder_name) and len(folder_name) != 0:
        os.makedirs(folder_name)

    # check hdf5 existence
    if os.path.exists(hdf5_name):
        # if already exists, open with r+ mode
        hdf5_file = h5py.File(hdf5_name, "r+")
        # check dataset existence
        if hdf5_path in hdf5_file:
            if is_overwrite:
                logging.warning(
                    "Dataset in hdf5 file already exists. " "recreate dataset in hdf5."
                )
                hdf5_file.__delitem__(hdf5_path)
            else:
                logging.error(
                    "Dataset in hdf5 file already exists. "
                    "if you want to overwrite, please set is_overwrite = True."
                )
                hdf5_file.close()
                sys.exit(1)
    else:
        # if not exists, open with w mode
        hdf5_file = h5py.File(hdf5_name, "w")

    # write data to hdf5
    hdf5_file.create_dataset(hdf5_path, data=write_data)
    hdf5_file.flush()
    hdf5_file.close()

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

        class objectview(object):
            def __init__(self, d):
                self.__dict__ = d
        config = objectview(config)

    else:
        raise Exception(
            "Configuration type not yet supported, only python modules are taken into accounts"
        )

    return config


###############################################################################
# Utils
###############################################################################

def normalize(S: np.ndarray, config):
    return np.clip((S - config.min_level_db) / -config.min_level_db, 0, 1)


def denormalize(S: np.ndarray, config):
    return (np.clip(S, 0, 1) * -config.min_level_db) + config.min_level_db


def amp_to_db(x: np.ndarray):
    return 20 * np.log10(np.maximum(1e-5, x))


def db_to_amp(x: np.ndarray):
    return np.power(10.0, x * 0.05)

###############################################################################
# Extraction
###############################################################################


def wav2mel(x: np.ndarray, config, eps=1e-10) -> np.ndarray:
    """Extract mel spectrogram from the given signal

    Largely adapted from https://github.com/kan-bayashi/ParallelWaveGAN/blob/master/parallel_wavegan/bin/preprocess.py

    """
    # get amplitude spectrogram
    x_stft = librosa.stft(
        x,
        n_fft=config.fft_size,
        hop_length=config.hop_size,
        win_length=config.win_length,
        window=config.window,
        pad_mode="reflect",
    )
    spc = np.abs(x_stft).T  # (#frames, #bins)

    # get mel basis
    fmin = 0 if config.fmin is None else config.fmin
    fmax = sampling_rate / 2 if config.fmax is None else config.fmax
    mel_basis = librosa.filters.mel(config.sampling_rate, config.fft_size, config.num_mels, fmin, fmax)
    mel = np.maximum(eps, np.dot(spc, mel_basis.T))

    if config.scale == "ln":
        return np.log(mel)
    elif config.scale == "log10":
        return np.log10(mel)
    elif config.scale == "log2":
        return np.log2(mel)
    elif config.scale == "db":
        return amp_to_db(mel)
    else:
        raise ValueError(f"{scale} is not supported.")

###############################################################################
# Neural vocoder helpers & entry function
###############################################################################


def save_wavegan(mel_spectrogram: np.ndarray, output_file: str):
    """Help to save the spectrogram to be compatible with WaveGAN (TODO: repo)

    WaveGAN loads spectrograms saved in the hdf5 format using the shape (nb_mel, nb_frames).
    WaveGAN considers two "paths" in the hdf5 file:
    	- feats :: for the features
        - ??? :: for the quantized waveform

    In this script, we only consider the path "feats".
    If the file already exists, the feats path is added to the existing content.
    A word of caution: the path "feats" will be overwritten if already exists!

    Parameters
    ----------
    mel_spectrogram: np.ndarray
    	The mel spectrogram in the numpy format

    output_file: str
    	The output filename
    """
    write_hdf5(output_file, "feats", mel_spectrogram, True)

def save_wavenet(mel_spectrogram: np.ndarray, output_file: str):
    """Help to save the spectrogram to be compatible with WaveNet (TODO: repo)

    WaveNet loads spectrograms saved in the numpy format using the shape (nb_mel, nb_frames)

    Parameters
    ----------
    mel_spectrogram: np.ndarray
    	The mel spectrogram in the numpy format

    output_file: str
    	The output filename
    """
    np.save(output_file, mel_spectrogram.T)

def save_wavernn(mel_spectrogram: np.ndarray, output_file: str):
    """Help to save the spectrogram to be compatible with WaveRNN (TODO: repo)

    WaveRNN loads spectrograms saved in the numpy format using the shape (nb_mel, nb_frames)

    Parameters
    ----------
    mel_spectrogram: np.ndarray
    	The mel spectrogram in the numpy format

    output_file: str
    	The output filename
    """
    np.save(output_file, mel_spectrogram)

def save_waveglow(mel_spectrogram: np.ndarray, output_file: str):
    """Help to save the spectrogram to be compatible with WaveGLOW (TODO: repo)

    WaveGLOW loads spectrogram saved in standard PyTorch format using the shape (nb_mel, nb_frames)

    Parameters
    ----------
    mel_spectrogram: np.ndarray
    	The mel spectrogram in the numpy format

    output_file: str
    	The output filename
    """
    torch.save(torch.Tensor(mel_spectrogram), output_file)


def parametrize_wavfile(
    wav_file: str, output_directory: str, config, parametrization_type: str
):

    global logger

    # Load wav
    x, _ = librosa.load(wav_file, sr=config.sampling_rate)

    # Extract the mel spectrogram
    data = wav2mel(x, config)

    # Save it
    # - WaveGAN - TODO: add repo URL
    if parametrization_type == "wg":
        logger.debug(f"Save the spectrogram extracted from {Path(wav_file).stem} to be compatible with Parallel WaveGAN")
        output_filename = os.path.join(output_directory, Path(wav_file).stem + ".h5")
        save_wavegan(data, output_filename)

    # - WaveGlow - TODO: add repo URL
    elif parametrization_type == "wG":
        logger.debug(f"Save the spectrogram extracted from {Path(wav_file).stem} to be compatible with WaveGlow")
        output_filename = os.path.join(output_directory, Path(wav_file).stem + ".pt")
        save_waveglow(data, output_filename)

    # - WaveNet - TODO: add repo URL
    elif parametrization_type == "wn":
        logger.debug(f"Save the spectrogram extracted from {Path(wav_file).stem} to be compatible with WaveNet")
        output_filename = os.path.join(
            output_directory, Path(wav_file).stem + "-feats.npy"
        )
        save_wavenet(data, output_filename)

    # - WaveRNN - TODO: add repo URL
    elif parametrization_type == "wr":
        logger.debug(f"Save the spectrogram extracted from {Path(wav_file).stem} to be compatible with WaveRNN")
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
