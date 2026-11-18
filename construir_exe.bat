@echo off
REM Genera los ejecutables de Windows con PyInstaller.
REM Resultado en la carpeta dist\ :
REM   CalculadoraIP.exe    (ambas calculadoras en pestañas)
REM   CalculadoraCIDR.exe  (solo CIDR)
REM   CalculadoraVLSM.exe  (solo VLSM)
cd /d "%~dp0"
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")

echo [1/4] Instalando PyInstaller...
%PY% -m pip install --upgrade pyinstaller || goto error

echo [2/4] Ejecutando pruebas antes de empaquetar...
%PY% -m unittest discover -s tests -t . || goto error

set "OPCIONES=--noconfirm --onefile --windowed --clean --hidden-import interfaz.gui --hidden-import interfaz.consola"

echo [3/4] Construyendo ejecutables...
%PY% -m PyInstaller %OPCIONES% --name CalculadoraIP   main.py              || goto error
%PY% -m PyInstaller %OPCIONES% --name CalculadoraCIDR calculadora_cidr.py  || goto error
%PY% -m PyInstaller %OPCIONES% --name CalculadoraVLSM calculadora_vlsm.py  || goto error

echo [4/4] Listo. Los ejecutables estan en la carpeta dist\
explorer dist
pause
exit /b 0

:error
echo.
echo Ocurrio un error durante la construccion. Revisa los mensajes de arriba.
pause
exit /b 1
