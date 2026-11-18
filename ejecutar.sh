#!/usr/bin/env sh
# Abre la Calculadora IP en Linux o macOS.
#   ./ejecutar.sh            -> interfaz gráfica
#   ./ejecutar.sh --consola  -> menú de texto
cd "$(dirname "$0")" || exit 1
python3 main.py "$@"
