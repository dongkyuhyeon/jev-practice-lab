@echo off
setlocal
cd /d "%~dp0"
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama is not installed or not on PATH.
  echo Install Ollama 0.35.0 or later, then run: ollama pull tev1:0.8b
  exit /b 1
)
ollama --version
ollama list
python decision_lab.py --backend ollama --model tev1:0.8b --scenario agent-gate "git status"
