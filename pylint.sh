#!/bin/bash
export PYRIGHT_PYTHON_FORCE_VERSION=latest

echo "Pyright ..."
python -m pyright .
echo "Ruff ..."
python -m ruff check --exclude pytests .
echo "Mypy ..."
python -m mypy --explicit-package-bases --warn-return-any --check-untyped-defs --exclude loadtest --exclude tests .
