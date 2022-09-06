# File
import os

# Math
import torch
import numpy as np

# Arguments
import argparse

###############################################################################
# Functions
###############################################################################
HTK_UNIT_MS = 10000
MERLIN_DEFAULT_FRAME_RATE = 5
FASTPITCH_DEFAULT_FRAME_RATE = 5
NB_STATES=5

parser = argparse.ArgumentParser(description="")
parser.add_argument("file_list", help="The label file generated for merlin")
parser.add_argument("f0_dir", help="The f0 file extracted for merlin")
parser.add_argument("normalized_f0_dir", help="The f0 file extracted for merlin")
parser.add_argument("normalized_info_json_file", help="The f0 file extracted for merlin")
args = parser.parse_args()

# Load file list
with open(args.file_list) as f:
    basenames = [l.strip() for l in f]

# Load everything
f0_file_contents = []
for basename in basenames:
    f0 = torch.load(os.path.join(args.f0_dir, f"{basename}.pt")).numpy()
    f0_file_contents.append(f0)

# Compute normalization parameters
f0_voiced = np.concatenate([f0[f0>0] for f0 in f0_file_contents])
mean = np.mean(f0_voiced)
std = np.std(f0_voiced)

# Normalize
for i_file, f0_values in enumerate(f0_file_contents):
    # Save unvoiced indices
    zero_idx = np.where(f0_values == 0)

    # Normalize voiced
    f0_values -= mean
    f0_values /= std

    # Set unvoiced segment to 0
    f0_values[zero_idx] = 0

    # Save normalizer
    f0_tensor = torch.Tensor(f0_values)
    torch.save(f0_tensor, os.path.join(args.normalized_f0_dir, f"{basenames[i_file]}.pt"))

with open(args.normalized_info_json_file, "w") as f_out:
    f_out.write(f"{{ \"mean\": {mean}, \"std\": {std} }}")
