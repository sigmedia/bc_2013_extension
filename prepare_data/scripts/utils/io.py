# Python
import sys
import os
from pathlib import Path
from typing import List

# Messaging/logging
import logging

# IO
import h5py
import yaml

# Data
import numpy as np
import torch

# Audio/signal processing
from scipy import signal
import librosa

###############################################################################
# HDF5 Wrappers
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


###############################################################################
# WaveGAN
###############################################################################
def load_wavegan(input_file: str, path: str="feats") -> np.ndarray:
    """TODO"""
    assert path in ("feats", "wave")
    return read_hdf5(input_file, path)

def save_wavegan(mel_spectrogram: np.ndarray, output_file: str, path: str="feats"):
    """Help to save the spectrogram to be compatible with WaveGAN (TODO: repo)

    WaveGAN loads spectrograms saved in the hdf5 format using the shape (nb_mel, nb_frames).
    WaveGAN considers two "paths" in the hdf5 file:
    	- feats :: for the features
        - wave :: for the quantized waveform

    If the file already exists, the path is added to the existing content.
    A word of caution: the path will be overwritten if already exists!

    Parameters
    ----------
    mel_spectrogram: np.ndarray
    	The mel spectrogram in the numpy format

    output_file: str
    	The output filename
    """
    assert path in ("feats", "wave")
    write_hdf5(output_file, path, mel_spectrogram, True)


###############################################################################
# WaveNet
###############################################################################
def load_wavenet(input_file: str) -> np.ndarray:
    """TODO
    """
    return np.load(input_file)


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
    np.save(output_file, mel_spectrogram)

###############################################################################
# WaveGlow
###############################################################################

def load_waveglow(input_file: str) -> np.ndarray:
    """TODO
    """
    return torch.load(input_file).numpy()

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


###############################################################################
# WaveRNN
###############################################################################

def load_wavernn(input_file: str) -> np.ndarray:
    """TODO
    """
    return np.load(input_file)

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


###############################################################################
# FastPitch
###############################################################################

def load_tacotron(input_file: str) -> np.ndarray:
    """TODO
    """

    return np.load(input_file).T

def save_tacotron(mel_spectrogram: np.ndarray, output_file: str):
    """Help to save the spectrogram to be compatible with WaveRNN (TODO: repo)

    WaveRNN loads spectrograms saved in the numpy format using the shape (nb_mel, nb_frames)

    Parameters
    ----------
    mel_spectrogram: np.ndarray
    	The mel spectrogram in the numpy format

    output_file: str
    	The output filename
    """
    np.save(output_file, mel_spectrogram.T)
