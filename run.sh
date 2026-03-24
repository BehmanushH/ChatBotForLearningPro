#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
elif [[ -x "venv/bin/python" ]]; then
  PY="venv/bin/python"
else
  python3 -m venv .venv
  PY=".venv/bin/python"
fi

"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r requirements.txt
"$PY" -m streamlit run app.py

