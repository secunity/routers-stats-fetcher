venv_name=venv
echo $venv_name
python3.7 -m venv $venv_name
virtualenv --python=python3.7 $venv_name
source venv/bin/activate
python3.7  -m pip install -r requirements.txt
