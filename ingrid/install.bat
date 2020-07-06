call conda create -y -n model-processing python=3.6
call activate model-processing && python -V
call python -m pip install --upgrade pip
call pip install -r requirements-dev.txt
