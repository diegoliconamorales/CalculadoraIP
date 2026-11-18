"""
calculadora_vlsm.py
-------------------
Abre únicamente la Calculadora VLSM. Con PyInstaller se convierte en
CalculadoraVLSM.exe.
"""

from main import iniciar_interfaz

if __name__ == "__main__":
    iniciar_interfaz("vlsm")
