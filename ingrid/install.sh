#!/bin/bash

conda create -y -n model_processing python=3.6
conda activate model_processing
if [ "$?" != 0 ]; then
  FILE=~/anaconda3/etc/profile.d/conda.sh
  if [ ! -f "$FILE" ]; then
    FILE=~/miniconda3/etc/profile.d/conda.sh
    if [ ! -f "$FILE" ]; then
      echo "Failure executing conda activate. see recommendation above. Exiting"
      exit
    fi
  fi
  source $FILE
  conda activate model_processing
  if [ "$?" != 0 ]; then
    echo "Failure executing conda activate. see recommendation above. Exiting"
    exit
  else
    echo "Successfully activated model_processing environment"
  fi
fi
python -m pip install -e . --ignore-installed
