@echo off
REM Abre la Calculadora IP en modo texto (menu en la terminal).
cd /d "%~dp0"
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
%PY% main.py --consola
pause
