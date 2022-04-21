import torch
from models.fatchord_version import WaveRNN
from utils import hparams as hp
from utils.text.symbols import symbols
from models.tacotron import Tacotron
import argparse
from utils.text import text_to_sequence
from utils.display import save_attention, simple_table
import zipfile, os

# Test Example:
# python test_taco_model_auto.py --checkpoint blizzard_baseline_JE.tacotron/final_taco_300K.pyt --model_name JE_fixed


if __name__ == "__main__":

    # Parse Arguments
    parser = argparse.ArgumentParser(description='TTS Generator')
    parser.add_argument('--input_text', '-i', type=str, help='[string] Type in something here and TTS will generate it!')
    parser.add_argument('--batched', '-b', dest='batched', action='store_true', help='Fast Batched Generation (lower quality)')
    parser.add_argument('--unbatched', '-u', dest='batched', action='store_false', help='Slower Unbatched Generation (better quality)')
    parser.add_argument('--force_cpu', '-c', action='store_true', help='Forces CPU-only training, even when in CUDA capable environment')
    parser.add_argument('--hp_file', metavar='FILE', default='hparams.py',
                        help='The file to use for the hyperparameters')
    parser.add_argument('--checkpoint', metavar='FILE', required = True,
                        help='The checkpoint you want to synthesise from')
    parser.add_argument('--model_name', metavar='FILE', required = True,
                        help='The model name to save synthesised files')
    args = parser.parse_args()

    hp.configure(args.hp_file)  # Load hparams from file

    parser.set_defaults(batched=True)
    parser.set_defaults(input_text=None)

    batched = args.batched
    input_text = args.input_text
    checkpoint = args.checkpoint
    model_name = args.model_name

    if not args.force_cpu and torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')
    print('Using device:', device)

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
                        mode='MOL').to(device)

    voc_model.load('quick_start/voc_weights/latest_weights.pyt')

    print('\nInitialising Tacotron Model...\n')

    # Instantiate Tacotron Model
    tts_model = Tacotron(embed_dims=hp.tts_embed_dims,
                         num_chars=len(symbols),
                         encoder_dims=hp.tts_encoder_dims,
                         decoder_dims=hp.tts_decoder_dims,
                         n_mels=hp.num_mels,
                         fft_bins=hp.num_mels,
                         postnet_dims=hp.tts_postnet_dims,
                         encoder_K=hp.tts_encoder_K,
                         lstm_dims=hp.tts_lstm_dims,
                         postnet_K=hp.tts_postnet_K,
                         num_highways=hp.tts_num_highways,
                         dropout=hp.tts_dropout,
                         stop_threshold=hp.tts_stop_threshold).to(device)


    tts_model.load(f'checkpoints/{checkpoint}')

    if input_text:
        inputs = [text_to_sequence(input_text.strip(), hp.tts_cleaner_names)]
    else:
        with open('phoneme_test.txt') as f:
            inputs = [text_to_sequence(l.strip(), hp.tts_cleaner_names) for l in f]

    voc_k = voc_model.get_step() // 1000
    tts_k = tts_model.get_step() // 1000

    r = tts_model.r

    simple_table([('WaveRNN', str(voc_k) + 'k'),
                  (f'Tacotron(r={r})', str(tts_k) + 'k'),
                  ('Generation Mode', 'Batched' if batched else 'Unbatched'),
                  ('Target Samples', 11_000 if batched else 'N/A'),
                  ('Overlap Samples', 550 if batched else 'N/A')])

    for i, x in enumerate(inputs, 1):

        print(f'\n| Generating {i}/{len(inputs)}')
        _, m, attention = tts_model.generate(x)

        if input_text:
            save_path = f'gen_output/__input_{input_text[:10]}_{tts_k}k.wav'
        else:
            save_path = f'gen_output/{i}_{tts_k}k_{model_name}.wav'


        m = torch.tensor(m).unsqueeze(0)
        m = (m + 4) / 8

        voc_model.generate(m, save_path, batched, 11_000, 550, hp.mu_law)

    print('\n\nDone.\n')
