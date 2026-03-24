"""Quickstart helper for BanuCode Streamlit app."""

from __future__ import annotations

import os
import subprocess
import sys


def _venv_python() -> str:
	if os.name == "nt":
		return os.path.join(".venv", "Scripts", "python.exe")
	return os.path.join(".venv", "bin", "python")


def main() -> int:
	if not os.path.exists(_venv_python()):
		subprocess.check_call([sys.executable, "-m", "venv", ".venv"])

	py = _venv_python()
	subprocess.check_call([py, "-m", "pip", "install", "--upgrade", "pip"])
	subprocess.check_call([py, "-m", "pip", "install", "-r", "requirements.txt"])
	subprocess.check_call([py, "-m", "streamlit", "run", "app.py"])
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

