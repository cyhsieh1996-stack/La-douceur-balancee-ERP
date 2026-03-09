#!/bin/bash
cd "$(dirname "$0")"

# Prefer the known-good env first, then fallback to venv/system python.
if [ -x "./env/bin/python" ]; then
  ./env/bin/python main.py
elif [ -x "./venv/bin/python" ]; then
  ./venv/bin/python main.py
else
  python3 main.py
fi
