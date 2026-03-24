@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
  set "PY=venv\Scripts\python.exe"
) else (
  py -m venv .venv
  set "PY=.venv\Scripts\python.exe"
)

"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
"%PY%" -m streamlit run app.py

endlocal

