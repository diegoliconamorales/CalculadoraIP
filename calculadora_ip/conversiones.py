"""
conversiones.py
---------------
Funciones base para trabajar con direcciones IPv4 como ENTEROS de 32 bits.

Idea central del proyecto: una dirección IPv4 como 192.168.1.10 es en realidad
un número de 32 bits. Si la convertimos a entero, calcular la red, el broadcast
o el siguiente bloque se reduce a operaciones aritméticas y lógicas (AND, OR,
NOT, sumas), sin tener que manipular los cuatro octetos por separado.

Este módulo NO usa la biblioteca ipaddress: todas las conversiones y
validaciones están implementadas a mano para que el algoritmo sea visible.
"""

from __future__ import annotations

from .errores import ErrorEntrada

# 32 bits en 1: 11111111.11111111.11111111.11111111
MASCARA_32_BITS = 0xFFFFFFFF


# ---------------------------------------------------------------------------
# Conversión dotted-decimal  <->  entero de 32 bits
# ---------------------------------------------------------------------------
def ip_a_entero(texto: str) -> int:
    """
    Convierte una IP en notación decimal punteada a un entero de 32 bits.

    Ejemplo: "192.168.1.10" -> (192 << 24) | (168 << 16) | (1 << 8) | 10
                            -> 3232235786

    Valida que existan exactamente 4 octetos, que cada uno sea numérico
    y que esté en el rango 0-255. Lanza ErrorEntrada con un mensaje claro
    si algo no es válido.
    """
    texto = (texto or "").strip()
    if not texto:
        raise ErrorEntrada("No se escribió ninguna dirección IP.")

    octetos = texto.split(".")
    if len(octetos) != 4:
        raise ErrorEntrada(
            f"La dirección '{texto}' debe tener 4 octetos separados por puntos "
            f"(ejemplo: 192.168.1.10)."
        )

    valor = 0
    for posicion, octeto in enumerate(octetos, start=1):
        octeto = octeto.strip()
        if not octeto.isdigit():
            raise ErrorEntrada(
                f"El octeto {posicion} ('{octeto}') de '{texto}' no es un número entero."
            )
        numero = int(octeto)
        if numero > 255:
            raise ErrorEntrada(
                f"El octeto {posicion} de '{texto}' vale {numero}; "
                f"cada octeto debe estar entre 0 y 255."
            )
        # Desplazamos lo acumulado 8 bits a la izquierda y "pegamos" el octeto.
        valor = (valor << 8) | numero
    return valor


def entero_a_ip(valor: int) -> str:
    """
    Convierte un entero de 32 bits de vuelta a notación decimal punteada.

    Se aíslan los 4 octetos desplazando a la derecha 24, 16, 8 y 0 bits
    y aplicando AND con 255 (0xFF) para quedarnos solo con 8 bits.
    """
    if not 0 <= valor <= MASCARA_32_BITS:
        raise ErrorEntrada(f"El valor {valor} no cabe en 32 bits.")
    return ".".join(str((valor >> desplazamiento) & 0xFF) for desplazamiento in (24, 16, 8, 0))


# ---------------------------------------------------------------------------
# Prefijos y máscaras
# ---------------------------------------------------------------------------
def prefijo_a_mascara(prefijo: int) -> int:
    """
    Genera la máscara (como entero) a partir del prefijo /n.

    Se desplaza un bloque de 32 unos (32 - n) posiciones a la izquierda,
    lo que deja n unos seguidos de (32 - n) ceros.
    Ejemplo /24: 0xFFFFFFFF << 8 = 11111111.11111111.11111111.00000000
    """
    validar_prefijo(prefijo)
    if prefijo == 0:
        return 0
    return (MASCARA_32_BITS << (32 - prefijo)) & MASCARA_32_BITS


def mascara_a_prefijo(texto_mascara: str) -> int:
    """
    Convierte una máscara decimal punteada (255.255.255.0) a prefijo (/24).

    Una máscara válida debe tener todos sus unos juntos a la izquierda.
    Para comprobarlo se invierte la máscara (NOT): el resultado debe ser
    de la forma 000...0111...1, y un número así cumple que
    invertida & (invertida + 1) == 0.
    """
    mascara = ip_a_entero(texto_mascara)
    invertida = ~mascara & MASCARA_32_BITS
    if invertida & (invertida + 1) != 0:
        raise ErrorEntrada(
            f"La máscara '{texto_mascara}' no es válida: sus bits en 1 deben ser "
            f"contiguos (por ejemplo 255.255.255.0 o 255.255.240.0)."
        )
    return bin(mascara).count("1")


def validar_prefijo(prefijo: int) -> None:
    """Verifica que el prefijo esté entre 0 y 32."""
    if not isinstance(prefijo, int) or not 0 <= prefijo <= 32:
        raise ErrorEntrada(f"El prefijo /{prefijo} no es válido; debe estar entre /0 y /32.")


def leer_prefijo_o_mascara(texto: str) -> int:
    """
    Acepta el segundo dato de la calculadora en cualquiera de sus formas:
      "24", "/24"            -> prefijo
      "255.255.255.0"        -> máscara decimal punteada
    y siempre devuelve el prefijo como entero.
    """
    texto = (texto or "").strip()
    if not texto:
        raise ErrorEntrada("Falta el prefijo o la máscara (ejemplo: /24 o 255.255.255.0).")
    if "." in texto:
        return mascara_a_prefijo(texto)
    sin_diagonal = texto.lstrip("/").strip()
    if not sin_diagonal.isdigit():
        raise ErrorEntrada(f"'{texto}' no es un prefijo válido (ejemplo: /24).")
    prefijo = int(sin_diagonal)
    validar_prefijo(prefijo)
    return prefijo


def interpretar_red(texto: str, segundo_dato: str = "") -> tuple[int, int]:
    """
    Interpreta la entrada del usuario y devuelve (ip_entera, prefijo).

    Formas aceptadas:
      interpretar_red("192.168.1.10/24")
      interpretar_red("192.168.1.10/255.255.255.0")
      interpretar_red("192.168.1.10 255.255.255.0")
      interpretar_red("192.168.1.10", "/24")  o  ("192.168.1.10", "255.255.255.0")
    """
    texto = (texto or "").strip()
    segundo_dato = (segundo_dato or "").strip()

    if "/" in texto:
        ip_txt, resto = texto.split("/", 1)
        if segundo_dato:
            raise ErrorEntrada("El prefijo se indicó dos veces; escríbelo solo en un campo.")
        segundo_dato = resto
    elif " " in texto and not segundo_dato:
        ip_txt, segundo_dato = texto.split(None, 1)
    else:
        ip_txt = texto

    if not segundo_dato:
        raise ErrorEntrada(
            "Falta el prefijo o la máscara. Escribe por ejemplo 192.168.1.0/24 "
            "o 192.168.1.0 con la máscara 255.255.255.0."
        )
    return ip_a_entero(ip_txt), leer_prefijo_o_mascara(segundo_dato)


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------
def a_binario(valor: int, bits_resaltados: int | None = None) -> str:
    """
    Representa un entero de 32 bits en binario agrupado por octetos.

    Si se indica bits_resaltados (el prefijo), se marca con una barra '|'
    la frontera entre la porción de red y la porción de host. Si la frontera
    coincide con el fin de un octeto, la barra ocupa el lugar del punto.
    Ejemplos:
      192.168.1.10  /26 -> 11000000.10101000.00000001.00|001010
      255.255.255.0 /24 -> 11111111.11111111.11111111|00000000
    """
    bits = format(valor, "032b")
    salida = []
    for posicion, bit in enumerate(bits):
        if posicion and posicion == bits_resaltados:
            salida.append("|")             # frontera red | host
        elif posicion and posicion % 8 == 0:
            salida.append(".")             # separación entre octetos
        salida.append(bit)
    return "".join(salida)


def clase_de_ip(ip: int) -> str:
    """Clase según el modelo classful (por el primer octeto)."""
    primer_octeto = ip >> 24
    if primer_octeto == 0:
        return "Reservada (0.x.x.x)"
    if primer_octeto <= 126:
        return "A"
    if primer_octeto == 127:
        return "Loopback (127.x.x.x)"
    if primer_octeto <= 191:
        return "B"
    if primer_octeto <= 223:
        return "C"
    if primer_octeto <= 239:
        return "D (Multicast)"
    return "E (Experimental)"


def tipo_de_ip(ip: int) -> str:
    """Indica si la dirección es privada (RFC 1918), pública u otro uso especial."""
    rangos = [
        ("10.0.0.0", 8, "Privada (RFC 1918)"),
        ("172.16.0.0", 12, "Privada (RFC 1918)"),
        ("192.168.0.0", 16, "Privada (RFC 1918)"),
        ("127.0.0.0", 8, "Loopback"),
        ("169.254.0.0", 16, "Link-local (APIPA)"),
        ("100.64.0.0", 10, "Compartida CGNAT (RFC 6598)"),
        ("224.0.0.0", 4, "Multicast"),
        ("240.0.0.0", 4, "Reservada"),
        ("0.0.0.0", 8, "Reservada"),
    ]
    for red_txt, prefijo, nombre in rangos:
        mascara = prefijo_a_mascara(prefijo)
        if ip & mascara == ip_a_entero(red_txt):
            return nombre
    return "Pública"
