# Blizzard 2013-EH2 extension - Replikant configuration

Replikant configuration to run the Blizzard 2013 - EH2 extension test conducted and analyzed in [Le Maguer, 2024]

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
@article{LeMaguer2024,
    title        = {{The limits of the Mean Opinion Score for speech synthesis evaluation}},
    author       = {Sébastien {Le Maguer} and Simon King and Naomi Harte},
    year         = 2024,
    journal      = {Computer, Speech \& Language},
    volume       = 84,
    pages        = 101577,
    doi          = {https://doi.org/10.1016/j.csl.2023.101577},
    issn         = {0885-2308},
    url          = {https://www.sciencedirect.com/science/article/pii/S0885230823000967},
}
```
