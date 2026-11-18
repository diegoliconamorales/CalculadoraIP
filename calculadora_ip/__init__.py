"""
Paquete calculadora_ip: lógica de cálculo (sin interfaz) de la Calculadora IP.

- conversiones: IP <-> entero, prefijo <-> máscara, binario, clase.
- cidr:         Calculadora IP (CIDR) para una dirección + prefijo/máscara.
- vlsm:         Calculadora VLSM para una red base y una lista de requerimientos.
"""

from .errores import ErrorEntrada
from .cidr import ResultadoCIDR, calcular_cidr, calcular_cidr_desde_texto
from .vlsm import Requerimiento, SubredAsignada, ResultadoVLSM, calcular_vlsm

__version__ = "1.0.0"

__all__ = [
    "ErrorEntrada",
    "ResultadoCIDR", "calcular_cidr", "calcular_cidr_desde_texto",
    "Requerimiento", "SubredAsignada", "ResultadoVLSM", "calcular_vlsm",
]
