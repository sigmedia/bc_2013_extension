# Blizzard 2013-EH2 extension - Replikant configuration

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
