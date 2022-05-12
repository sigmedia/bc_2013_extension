# Parametrical acoustic/articulatory speech synthesis

The goal of this repository is to show how to use the different gradle plugins to achieve a full HTS training/synthesis/analysis process.


## Repository architecture

The repository is divided into 4 main project directories:

-   **extraction** which contains the coefficient extraction project.
-   **training** which contains the model training project. This project should be run after the extraction project.
-   **synthesis** which contains the test corpus synthesis project. This project should be run after the training project.
-   **analysis** which contains the analysis project. This project should be run after the synthesis **and** extraction projects.

A special directory has been created to store the configuration files **src/configuration/**


## How to Run

```sh
# Some example parameters
export NB_PROC=2
export EVAL_NAME=cmu_slt_arctic_straight_dnn
(cd 10-extraction; ./gradlew b --parallel --max-workers=$NB_PROC -Deval_name=$EVAL_NAME)
(cd 20-training; ./gradlew b --parallel --max-workers=$NB_PROC -Deval_name=$EVAL_NAME)
(cd 30-synthesis; ./gradlew b --parallel --max-workers=$NB_PROC -Deval_name=$EVAL_NAME)
(cd 40-analysis; ./gradlew b --parallel --max-workers=$NB_PROC -Deval_name=$EVAL_NAME)
```


## References
