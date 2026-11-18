"""
cidr.py
-------
Calculadora IP (CIDR).

Entrada : una dirección IP y su prefijo (/n) o máscara decimal.
Salida  : dirección de red, broadcast, rango de hosts, máscara, wildcard,
          número de hosts válidos, clase, tipo y representación binaria.

Todo el cálculo se hace con la IP convertida a entero de 32 bits:
    red       = ip AND máscara
    broadcast = red OR wildcard          (wildcard = NOT máscara)
    hosts     = 2^(32 - n) - 2
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .conversiones import (
    a_binario, clase_de_ip, entero_a_ip, interpretar_red,
    prefijo_a_mascara, tipo_de_ip, validar_prefijo, MASCARA_32_BITS,
)


@dataclass
class ResultadoCIDR:
    """Todos los datos calculados para una dirección IP con su prefijo."""
    ip: str
    prefijo: int
    mascara: str
    wildcard: str
    red: str
    broadcast: str
    primer_host: str
    ultimo_host: str
    total_direcciones: int
    hosts_validos: int
    clase: str
    tipo: str
    nota: str = ""
    binario: dict[str, str] = field(default_factory=dict)

    @property
    def red_cidr(self) -> str:
        return f"{self.red}/{self.prefijo}"

    @property
    def rango_hosts(self) -> str:
        if not self.primer_host:
            return "Sin hosts asignables"
        return f"{self.primer_host} - {self.ultimo_host}"


def calcular_cidr(ip: int, prefijo: int) -> ResultadoCIDR:
    """
    Calcula todos los parámetros de la red a la que pertenece `ip` con el
    prefijo dado. `ip` llega como entero de 32 bits.
    """
    validar_prefijo(prefijo)

    mascara = prefijo_a_mascara(prefijo)
    wildcard = ~mascara & MASCARA_32_BITS          # bits de host en 1
    red = ip & mascara                             # se apagan los bits de host
    broadcast = red | wildcard                     # se encienden los bits de host
    total = 2 ** (32 - prefijo)                    # tamaño del bloque

    # Rango de hosts según el tamaño del bloque
    nota = ""
    if prefijo <= 30:
        # Caso normal: se reservan la dirección de red y la de broadcast.
        primer, ultimo, hosts = red + 1, broadcast - 1, total - 2
    elif prefijo == 31:
        # RFC 3021: en enlaces punto a punto /31 ambas direcciones son usables.
        primer, ultimo, hosts = red, broadcast, 2
        nota = "Prefijo /31 (RFC 3021): enlace punto a punto, las 2 direcciones son usables."
    else:
        # /32 identifica a un solo equipo (ruta de host o loopback).
        primer, ultimo, hosts = red, red, 1
        nota = "Prefijo /32: identifica a un único equipo (ruta de host)."

    if not nota and ip == red:
        nota = "La dirección escrita es la dirección de red."
    elif not nota and ip == broadcast:
        nota = "La dirección escrita es la dirección de broadcast; no puede asignarse a un equipo."

    return ResultadoCIDR(
        ip=entero_a_ip(ip),
        prefijo=prefijo,
        mascara=entero_a_ip(mascara),
        wildcard=entero_a_ip(wildcard),
        red=entero_a_ip(red),
        broadcast=entero_a_ip(broadcast),
        primer_host=entero_a_ip(primer),
        ultimo_host=entero_a_ip(ultimo),
        total_direcciones=total,
        hosts_validos=hosts,
        clase=clase_de_ip(ip),
        tipo=tipo_de_ip(ip),
        nota=nota,
        binario={
            "IP": a_binario(ip, prefijo),
            "Máscara": a_binario(mascara, prefijo),
            "Wildcard": a_binario(wildcard, prefijo),
            "Red": a_binario(red, prefijo),
            "Broadcast": a_binario(broadcast, prefijo),
        },
    )


def calcular_cidr_desde_texto(texto: str, prefijo_o_mascara: str = "") -> ResultadoCIDR:
    """
    Punto de entrada para la interfaz: recibe el texto tal como lo escribió
    el usuario (por ejemplo "192.168.10.0/24", o "192.168.10.0" y
    "255.255.255.0") y devuelve el resultado completo.
    """
    ip, prefijo = interpretar_red(texto, prefijo_o_mascara)
    return calcular_cidr(ip, prefijo)
