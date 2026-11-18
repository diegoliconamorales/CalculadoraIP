@echo off
REM Abre la Calculadora IP (ventana con CIDR y VLSM) usando Python.
cd /d "%~dp0"
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
%PY% main.py
if errorlevel 1 (
  echo.
  echo No se pudo ejecutar. Verifica que Python 3.10 o superior este instalado
  echo y que se haya marcado "Add python.exe to PATH" al instalarlo.
  pause
)
