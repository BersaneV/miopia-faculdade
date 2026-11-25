#!/usr/bin/env bash
# Atalho para rodar o Miopia em Linux/macOS
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  . .venv/bin/activate
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
else
  . .venv/bin/activate
fi
python src/main.py "$@"
