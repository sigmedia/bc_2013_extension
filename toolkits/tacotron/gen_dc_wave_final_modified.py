import torch
from models.fatchord_version import WaveRNN
import hparams as hp
from utils.text.symbols import symbols
from utils.paths import Paths
from models.tacotron import Tacotron
import argparse
from utils.text import text_to_sequence
from utils.display import save_attention, simple_table
from utils.dsp import *
import os
import sys
from scipy import signal

if __name__ == "__main__" :

    # Parse Arguments
    parser = argparse.ArgumentParser(description='TTS Generator')
    parser.add_argument('--input_text', '-i', type=str, help='[string] Type in something here and TTS will generate it!')
    parser.add_argument('--batched', '-b', dest='batched', action='store_true', help='Fast Batched Generation')
    parser.add_argument('--unbatched', '-u', dest='batched', action='store_false', help='Slow Unbatched Generation')
    parser.add_argument('--target', '-t', type=int, help='[int] number of samples in each batch index')
    parser.add_argument('--overlap', '-o', type=int, help='[int] number of crossover samples')
    parser.add_argument('--weights_path', '-w', type=str, help='[string/path] Load in different Tacotron Weights')
    parser.add_argument('--save_attention', '-a', dest='save_attn', action='store_true', help='Save Attention Plots')
    parser.set_defaults(batched=hp.voc_gen_batched)
    parser.set_defaults(target=hp.voc_target)
    parser.set_defaults(overlap=hp.voc_overlap)
    parser.set_defaults(input_text=None)
    parser.set_defaults(weights_path=None)
    parser.set_defaults(save_attention=False)
    args = parser.parse_args()

    batched = args.batched
    target = args.target
    overlap = args.overlap
    input_text = args.input_text
    weights_path = args.weights_path
    save_attn = args.save_attention

    paths = Paths(hp.data_path, hp.voc_model_id, hp.tts_model_id)

    os.makedirs('quick_start/voc_weights/', exist_ok=True)

    zip_ref = zipfile.ZipFile('pretrained/ljspeech.wavernn.mol.800k.zip', 'r')
    zip_ref.extractall('quick_start/voc_weights/')
    zip_ref.close()

    print('\nInitialising WaveRNN Model...\n')

    # Instantiate WaveRNN Model
    voc_model = WaveRNN(rnn_dims=hp.voc_rnn_dims,
                        fc_dims=hp.voc_fc_dims,
                        bits=hp.bits,
                        pad=hp.voc_pad,
                        upsample_factors=hp.voc_upsample_factors,
                        feat_dims=hp.num_mels,
                        compute_dims=hp.voc_compute_dims,
                        res_out_dims=hp.voc_res_out_dims,
                        res_blocks=hp.voc_res_blocks,
                        hop_length=hp.hop_length,
                        sample_rate=hp.sample_rate,
                        mode=hp.voc_mode)

    voc_model.load('quick_start/voc_weights/latest_weights.pyt')



    voc_k = voc_model.get_step() // 1000

    simple_table([('WaveRNN', str(voc_k) + 'k'),
                  ('Generation Mode', 'Batched' if batched else 'Unbatched'),
                  ('Target Samples', target if batched else 'N/A'),
                  ('Overlap Samples', overlap if batched else 'N/A')])

    preemphasis = .97
    wfreq, hfilter = signal.freqz(b=[1],a=[1, -preemphasis],worN=1025,include_nyquist=True)
    hfilter = np.diag( abs(hfilter) )

    for filename in os.listdir("dc_mags"):
            print(filename)

            mag = np.load("dc_mags/%s"%filename)
            mag = mag.T


            mag = (np.clip(mag, 0, 1) * 100) - 100 + 20

            mag = np.power(10.0, mag * 0.05)

            mag = np.dot( hfilter , mag)

            mel = librosa.feature.melspectrogram(S=mag, sr=22050, n_fft=2048, n_mels=80)

            mel = 20* np.log10(np.maximum(1e-5, mel))

            mel = np.clip((mel  + 100) / 100,0,1)



            basename = filename[:-4]+'.wav'
            save_path = 'model_outputs/dc/%s'%basename


            m = torch.tensor(mel).unsqueeze(0)


            voc_model.generate(m, save_path, batched, hp.voc_target, hp.voc_overlap, hp.mu_law)
