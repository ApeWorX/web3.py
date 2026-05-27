#!/bin/bash

set -euo pipefail

python --version
rm -rf build dist
python -m build

temp_dir=$(mktemp -d)
cd "$temp_dir"
python -m venv venv-test
source venv-test/Scripts/activate
python -m pip install --upgrade "$(ls /c/Users/circleci/project/web3.py/dist/web3-*-py3-none-any.whl)" --progress-bar off
python - <<'PY'
import sys
from pathlib import Path

from web3 import Web3
import web3

python_path = str(Path(sys.executable)).replace('\\', '/')
web3_path = str(Path(web3.__file__)).replace('\\', '/')
assert 'venv-test' in python_path, python_path
assert 'venv-test' in web3_path, web3_path
assert Web3 is not None
PY
