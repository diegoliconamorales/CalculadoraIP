"""
vlsm.py
-------
Calculadora VLSM (Variable Length Subnet Mask).

Algoritmo (sigue el pseudocódigo de la guía del proyecto):
  1. Para cada subred: necesarias = hosts_requeridos + 2   (red + broadcast).
  2. Ordenar las subredes de mayor a menor.
  3. puntero = dirección de la red base (como entero de 32 bits).
  4. Para cada subred:
       bits_host  = ceil(log2(necesarias))
       prefijo    = 32 - bits_host
       bloque     = 2^bits_host
       red        = puntero
       primer     = red + 1
       último     = red + bloque - 2
       broadcast  = red + bloque - 1
       puntero    = puntero + bloque
  5. Si un broadcast rebasa el broadcast de la red base -> "espacio insuficiente".

Asignar de mayor a menor garantiza que cada bloque empiece en un múltiplo de
su propio tamaño, por lo que las subredes quedan contiguas y nunca se traslapan.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .conversiones import entero_a_ip, interpretar_red, prefijo_a_mascara, MASCARA_32_BITS
from .errores import ErrorEntrada


@dataclass
class Requerimiento:
    """Una subred solicitada por el usuario: nombre y hosts que necesita."""
    nombre: str
    hosts: int


@dataclass
class SubredAsignada:
    """Resultado de asignar un bloque a un requerimiento."""
    nombre: str
    hosts_solicitados: int
    prefijo: int
    mascara: str
    red: str
    primer_host: str
    ultimo_host: str
    broadcast: str
    tamano_bloque: int
    hosts_validos: int
    desperdicio: int          # hosts válidos que sobran: hosts_validos - hosts_solicitados

    @property
    def red_cidr(self) -> str:
        return f"{self.red}/{self.prefijo}"


@dataclass
class ResultadoVLSM:
    """Asignación completa más el resumen de uso de la red base."""
    red_base: str
    prefijo_base: int
    subredes: list[SubredAsignada]
    direcciones_totales: int
    direcciones_usadas: int
    siguiente_libre: str        # primera dirección no asignada ("" si se llenó)
    avisos: list[str] = field(default_factory=list)

    @property
    def direcciones_libres(self) -> int:
        return self.direcciones_totales - self.direcciones_usadas

    @property
    def porcentaje_usado(self) -> float:
        return 100.0 * self.direcciones_usadas / self.direcciones_totales

    @property
    def desperdicio_total(self) -> int:
        return sum(s.desperdicio for s in self.subredes)


def bits_de_host_para(hosts: int) -> int:
    """
    Número mínimo de bits de host para alojar `hosts` equipos.

    Equivale a ceil(log2(hosts + 2)), pero se calcula con bit_length() para
    evitar errores de redondeo de punto flotante:
      hosts = 100 -> necesarias = 102 -> (101).bit_length() = 7 -> /25
    """
    necesarias = hosts + 2
    return (necesarias - 1).bit_length()


def _validar_requerimientos(requerimientos: list[Requerimiento]) -> list[Requerimiento]:
    """Limpia y valida la lista; lanza ErrorEntrada con un mensaje claro."""
    if not requerimientos:
        raise ErrorEntrada("Agrega al menos una subred con su nombre y número de hosts.")

    limpios, vistos = [], set()
    for posicion, req in enumerate(requerimientos, start=1):
        nombre = str(req.nombre if req.nombre is not None else "").strip() or f"Subred {posicion}"
        if nombre.lower() in vistos:
            raise ErrorEntrada(f"El nombre '{nombre}' está repetido; cada subred debe tener un nombre distinto.")
        vistos.add(nombre.lower())

        try:
            hosts = int(str(req.hosts).strip())
        except (TypeError, ValueError):
            raise ErrorEntrada(f"Los hosts de '{nombre}' deben ser un número entero.") from None
        if hosts < 1:
            raise ErrorEntrada(f"La subred '{nombre}' debe pedir al menos 1 host.")
        limpios.append(Requerimiento(nombre, hosts))
    return limpios


def calcular_vlsm(red_base: str, requerimientos: list[Requerimiento]) -> ResultadoVLSM:
    """
    Asigna una subred a cada requerimiento dentro de `red_base`
    (por ejemplo "192.168.0.0/24") usando VLSM.
    """
    ip_base, prefijo_base = interpretar_red(red_base)
    lista = _validar_requerimientos(requerimientos)
    avisos: list[str] = []

    # La red base se normaliza a su dirección de red (AND con su máscara).
    mascara_base = prefijo_a_mascara(prefijo_base)
    inicio_base = ip_base & mascara_base
    fin_base = inicio_base | (~mascara_base & MASCARA_32_BITS)
    total_base = fin_base - inicio_base + 1
    if inicio_base != ip_base:
        avisos.append(
            f"{entero_a_ip(ip_base)} no es una dirección de red; "
            f"se usó la red {entero_a_ip(inicio_base)}/{prefijo_base}."
        )

    # Paso 2: ordenar de mayor a menor. sorted() es estable, así que si dos
    # subredes piden lo mismo conservan el orden en que se escribieron.
    lista = sorted(lista, key=lambda r: r.hosts, reverse=True)

    # Revisión previa: si la suma de bloques no cabe, se avisa de inmediato.
    requeridas = sum(2 ** bits_de_host_para(r.hosts) for r in lista)
    if requeridas > total_base:
        raise ErrorEntrada(
            f"Espacio insuficiente: las subredes necesitan {requeridas:,} direcciones "
            f"y la red {entero_a_ip(inicio_base)}/{prefijo_base} solo tiene {total_base:,}."
        )

    puntero = inicio_base                     # Paso 3
    subredes: list[SubredAsignada] = []

    for req in lista:                         # Paso 4
        bits_host = bits_de_host_para(req.hosts)
        prefijo = 32 - bits_host
        bloque = 2 ** bits_host

        # Protección adicional: el bloque debe empezar en un múltiplo de su tamaño.
        # Con el orden descendente siempre se cumple, pero se comprueba por seguridad.
        if (puntero - inicio_base) % bloque:
            puntero += bloque - (puntero - inicio_base) % bloque

        red = puntero
        broadcast = red + bloque - 1

        # Paso 5: control de desbordamiento
        if broadcast > fin_base:
            raise ErrorEntrada(
                f"Espacio insuficiente: la subred '{req.nombre}' ({req.hosts} hosts, /{prefijo}) "
                f"ya no cabe dentro de {entero_a_ip(inicio_base)}/{prefijo_base}."
            )

        hosts_validos = bloque - 2
        subredes.append(SubredAsignada(
            nombre=req.nombre,
            hosts_solicitados=req.hosts,
            prefijo=prefijo,
            mascara=entero_a_ip(prefijo_a_mascara(prefijo)),
            red=entero_a_ip(red),
            primer_host=entero_a_ip(red + 1),
            ultimo_host=entero_a_ip(broadcast - 1),
            broadcast=entero_a_ip(broadcast),
            tamano_bloque=bloque,
            hosts_validos=hosts_validos,
            desperdicio=hosts_validos - req.hosts,
        ))
        puntero = broadcast + 1               # el siguiente bloque inicia justo después

    usadas = puntero - inicio_base
    return ResultadoVLSM(
        red_base=entero_a_ip(inicio_base),
        prefijo_base=prefijo_base,
        subredes=subredes,
        direcciones_totales=total_base,
        direcciones_usadas=usadas,
        siguiente_libre=entero_a_ip(puntero) if puntero <= fin_base else "",
        avisos=avisos,
    )


def leer_requerimientos(texto: str) -> list[Requerimiento]:
    """
    Convierte texto como "Ventas=100, RH=50, Enlace1=2" en una lista de
    Requerimiento. Se usa en el modo consola.
    """
    requerimientos = []
    for parte in texto.replace(";", ",").split(","):
        parte = parte.strip()
        if not parte:
            continue
        if "=" in parte:
            nombre, hosts = parte.split("=", 1)
        elif ":" in parte:
            nombre, hosts = parte.split(":", 1)
        else:
            raise ErrorEntrada(f"'{parte}' debe escribirse como Nombre=hosts (ejemplo: Ventas=100).")
        requerimientos.append(Requerimiento(nombre.strip(), hosts.strip()))
    return requerimientos
