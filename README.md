# BanuCode (Streamlit)

BanuCode is a bilingual chatbot UI (English/Dari) for programming learning and employability support.

## What is fixed

- Project entry files restored (`app.py`, `llm_handler.py`, `translations.py`)
- Dependency manifest restored (`requirements.txt`)
- Launchers restored (`run.bat`, `run.sh`, `quickstart.py`)

## Quick run (Windows)

```powershell
cd "C:\Users\GitHub\SampleForOpenLLMs"
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

Or double-click `run.bat`.

## Quick run (macOS/Linux)

```bash
cd /path/to/SampleForOpenLLMs
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Or run `bash run.sh`.

## Notes

- Single backend model configuration is in `llm_handler.py`.
- Current response generation is placeholder text; you can wire real Hugging Face inference later.

