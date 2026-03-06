#!/usr/bin/env bash
set -euo pipefail

python --version
pip install --upgrade pip
pip install -r requirements.txt
# explicit safeguard in case service image has partial cached installs
pip install Flask
python -c "import flask; print('Flask ready:', flask.__version__)"
