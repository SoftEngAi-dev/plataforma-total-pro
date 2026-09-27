@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1 || (echo [ERROR] Python 3.10+ requerido.&pause&exit /b 1)
where node >nul 2>&1 || (echo [ERROR] Node.js LTS requerido para compilar la web.&pause&exit /b 1)
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
cd web
if not exist node_modules call npm install --no-audit --no-fund
call npm run build:local || (echo [ERROR] Build web fallo.&pause&exit /b 1)
cd ..
start "" http://127.0.0.1:8787/
python local_server.py --port 8787
