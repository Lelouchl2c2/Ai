@echo off
setlocal

echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
  echo Python not found. Install Python 3.10+ and re-run this script.
  exit /b 1
)

echo [2/4] Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
  echo Ollama not found. Please install from https://ollama.com/download
  exit /b 1
)

echo [3/4] Pulling base model Dolphin-2.8-Mistral-7B-v0.2...
ollama pull dolphin-mistral:7b-v2.8
if errorlevel 1 (
  echo Failed to pull dolphin-mistral:7b-v2.8
  exit /b 1
)

echo [4/4] Creating local model lilith-local from Modelfile...
ollama create lilith-local -f Modelfile
if errorlevel 1 (
  echo Failed to create lilith-local
  exit /b 1
)

echo Done. Run start_lilith.bat
