# Blizzard 2013-EH2 extension - Ranked Choice Voting (RCV) Test - Replikant configuration

Replikant configuration to run the Ranked Choice Voting (RCV) test conducted and analyzed in [Le Maguer, 2025].

## Preparing the environment and the test

First, it is required to install [replikant](https://github.com/seblemaguer/replikant). While the submission to pypi is in the pipeline, in between, you can install it using the following command:

```sh
pip install git+https://github.com/seblemaguer/replikant.git
```

You also need to populate the test, by retrieving the samples to evaluate:

```sh
bash -xe populate.sh
```

## Start the test

```sh
replikant structure.yaml
```

## Reference

```bibtex
@inproceedings{lemaguer25_ssw,
  title     = {Speech Synthesis Evaluation from a voting perspective - a starting point},
  author    = {Sébastien {Le Maguer} and Juraj Šimko},
  year      = {2025},
  booktitle = {13th edition of the Speech Synthesis Workshop},
  pages     = {123--129},
  doi       = {10.21437/SSW.2025-19},
}
```
