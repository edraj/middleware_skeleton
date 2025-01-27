#!/bin/sh

# # Activate the virtual environment
# source ~/.venv/bin/activate

# # Run the Hypercorn command
# python3 -m hypercorn main:app --config file:utils/hypercorn_config.py


$HOME/venv/bin/python3 -m hypercorn main:app --config file:utils/hypercorn_config.py
