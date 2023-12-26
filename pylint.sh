#!/bin/bash

echo "Pyright ..."
# PYRIGHT_PYTHON_FORCE_VERSION=latest
python -m pyright
echo "Ruff ..."
python -m ruff check .
echo "Mypy ..."
python -m mypy --explicit-package-bases --warn-return-any .

