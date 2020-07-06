call conda create -y -n model_processing python=3.6
call activate model_processing && python -V
call python -m pip install -e . --ignore-installed
