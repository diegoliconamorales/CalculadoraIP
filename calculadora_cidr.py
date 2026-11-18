"""
calculadora_cidr.py
-------------------
Abre únicamente la Calculadora IP (CIDR). Con PyInstaller se convierte en
CalculadoraCIDR.exe.
"""

from main import iniciar_interfaz

if __name__ == "__main__":
    iniciar_interfaz("cidr")
