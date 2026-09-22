@echo off
REM ═══════════════════════════════════════════════════════════════════
REM  🚀 Plataforma Total — LEVANTAR LA APP WEB COMPLETA EN TU PC
REM  Doble clic y listo: frontend + backend real + base de datos local
REM  Requisitos una sola vez: Node.js LTS (https://nodejs.org) y Git
REM ═══════════════════════════════════════════════════════════════════
setlocal EnableDelayedExpansion
title Plataforma Total — servidor local
cd /d "%~dp0"

where node >nul 2>&1 || (echo ❌ Falta Node.js ^(https://nodejs.org^) — instalá y volvé a abrir este archivo. & pause & exit /b 1)
where git  >nul 2>&1 || (echo ❌ Falta Git ^(https://git-scm.com^) — instalá y volvé a abrir este archivo. & pause & exit /b 1)
where python >nul 2>&1 || (echo ⚠️ Sin Python: la web funciona igual; el desktop nativo lo pide. https://python.org)

echo 🔄 Actualizando código al último commit...
git fetch --all -q 2>nul && git reset --hard origin/main -q

cd web
if not exist node_modules (echo 📦 Instalando dependencias ^(solo la 1ra vez^)... & call npm install --no-audit --no-fund) else (echo 📦 Dependencias ok)

if not exist .dev.vars (
  echo ADMIN_SECRET=cambia-este-secreto> .dev.vars
  echo 🔐 Creado .dev.vars con secreto admin de pruebas ^(cambialo cuando quieras^)
)

echo 🗄️ Tablas de la base local...
call npx wrangler d1 execute plataforma --local --file=./schema.sql >nul 2>&1

echo 🏗️ Compilando la app...
set ASTRO_BASE=/
call npm run build || (echo ❌ Falló el build — revisá el error de arriba. & pause & exit /b 1)

echo.
echo ═══════════════════════════════════════════════════
echo  ✅ LISTO — la app completa corre en:
echo     http://localhost:8788   ^(se abre solo^)
echo  🔐 Secreto admin en web\.dev.vars  ·  Ctrl+C para apagar
echo ═══════════════════════════════════════════════════
echo.
start "" http://localhost:8788
call npx wrangler pages dev --port 8788
pause
