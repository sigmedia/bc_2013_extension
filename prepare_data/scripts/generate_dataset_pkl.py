import glob
from typing import Union, Dict
import pathlib
import pickle
import argparse
import numpy as np

def load_metadata(csv_file: str) -> Dict[str, str]:
    text_dict = {}
    with open(csv_file, encoding='utf-8') as f :
        for line in f :
            split = line.split('|')
            text_dict[split[0]] = split[-1]

    return text_dict


parser = argparse.ArgumentParser(description='Preprocessing for WaveRNN and Tacotron')
parser.add_argument('--metadata', '-m', help='directly point to location of CSV file')
parser.add_argument('--hp_file', metavar='FILE', default='hparams.py', help='The file to use for the hyperparameters')
parser.add_argument("mel_dir")
parser.add_argument("output_dir")
args = parser.parse_args()

mel_dir = pathlib.Path(args.mel_dir)
output_dir = pathlib.Path(args.output_dir)
text_dict = load_metadata(args.metadata)

dataset = []
for item_id in text_dict:
    m = np.load(mel_dir/f'{item_id}.npy')
    dataset += [(item_id, m.shape[-1])]

with open(output_dir/'text_dict.pkl', 'wb') as f:
    pickle.dump(text_dict, f)

with open(output_dir/'dataset.pkl', 'wb') as f:
    pickle.dump(dataset, f)
