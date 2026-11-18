@echo off
REM Ejecuta las pruebas unitarias del proyecto (carpeta tests).
cd /d "%~dp0"
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
%PY% -m unittest discover -s tests -t . -v
pause
