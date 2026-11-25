@echo off
REM Atalho para rodar o Miopia no Windows (duplo clique)
cd /d "%~dp0"
if not exist .venv (
  python -m venv .venv
  call .venv\Scripts\activate
  python -m pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
) else (
  call .venv\Scripts\activate
)
python src\main.py %*
pause
