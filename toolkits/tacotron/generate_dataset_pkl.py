import glob
from typing import Union
from utils.display import *
from utils.dsp import *
from utils import hparams as hp
from multiprocessing import Pool, cpu_count
from utils.paths import Paths, Path
import pickle
import argparse
from utils.text.recipes import blizzard
from utils.files import get_files


def csv2textdict(path: Union[str, Path]):
    csv_file = get_files(path, extension='.csv')

    assert len(csv_file) == 1

    text_dict = {}

    with open(csv_file[0], encoding='utf-8') as f :
        for line in f :
            split = line.split('|')
            text_dict[split[0]] = split[-1]

    return text_dict

# Helper functions for argument types
def valid_n_workers(num):
    n = int(num)
    if n < 1:
        raise argparse.ArgumentTypeError('%r must be an integer greater than 0' % num)
    return n


parser = argparse.ArgumentParser(description='Preprocessing for WaveRNN and Tacotron')
parser.add_argument('--path', '-p', help='directly point to location of CSV file')
parser.add_argument('--extension', '-e', metavar='EXT', default='.wav', help='file extension to search for in dataset folder')
parser.add_argument('--num_workers', '-w', metavar='N', type=valid_n_workers, default=cpu_count()-1, help='The number of worker threads to use for preprocessing')
parser.add_argument('--hp_file', metavar='FILE', default='hparams.py', help='The file to use for the hyperparameters')
args = parser.parse_args()

hp.configure(args.hp_file)  # Load hparams from file
if args.path is None:
    args.path = hp.wav_path

extension = args.extension
path = args.path


def process_wav(path: Path):
    wav_id = path.stem
    m = np.load(paths.mel/f'{wav_id}.npy')
    return wav_id, m.shape[-1]


wav_files = get_files(path, extension)
paths = Paths(hp.data_path, hp.voc_model_id, hp.tts_model_id)

print(f'\n{len(wav_files)} {extension[1:]} files found in "{path}"\n')

if len(wav_files) == 0:

    print('Please point wav_path in hparams.py to your dataset,')
    print('or use the --path option.\n')

else:

    if not hp.ignore_tts:

        text_dict = csv2textdict(path)

        with open(paths.data/'text_dict.pkl', 'wb') as f:
            pickle.dump(text_dict, f)

    n_workers = max(1, args.num_workers)

    simple_table([
        ('Sample Rate', hp.sample_rate),
        ('Bit Depth', hp.bits),
        ('Mu Law', hp.mu_law),
        ('Hop Length', hp.hop_length),
        ('CPU Usage', f'{n_workers}/{cpu_count()}')
    ])

    pool = Pool(processes=n_workers)
    dataset = []

    for i, (item_id, length) in enumerate(pool.imap_unordered(process_wav, wav_files), 1):
        dataset += [(item_id, length)]
        bar = progbar(i, len(wav_files))
        message = f'{bar} {i}/{len(wav_files)} '
        stream(message)

    with open(paths.data/'dataset.pkl', 'wb') as f:
        pickle.dump(dataset, f)

    print('\n\nCompleted. Ready to run "python train_tacotron.py" or "python train_wavernn.py". \n')
