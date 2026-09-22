@echo off
REM ═══════════════════════════════════════════════════════
REM  🖥️ Plataforma Total DESKTOP — correr desde el código
REM  (la forma rápida es instalar el .exe del release; esto es para tocar el código)
REM  Requisitos: Python 3.10+ (https://python.org → ✅ "Add to PATH")
REM ═══════════════════════════════════════════════════════
title Plataforma Total Desktop
cd /d "%~dp0"

where python >nul 2>&1 || (echo ❌ Falta Python ^(https://python.org — tildá "Add python to PATH"^) & pause & exit /b 1)

echo 🔄 Actualizando código...
git fetch --all -q 2>nul && git reset --hard origin/main -q

echo 📦 Dependencias (solo la 1ra vez)...
python -m pip install -r requirements.txt --quiet --disable-pip-version-warning

echo ✅ Abriendo Plataforma Total (57 cursos, 100%% offline)...
start "" pythonw main.py
exit /b 0
