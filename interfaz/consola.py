"""
consola.py
----------
Interfaz de texto de la Calculadora IP. Sirve como respaldo cuando no hay
entorno gráfico y para hacer pruebas rápidas desde la terminal.

Uso directo (sin menú):
    python main.py --cidr 192.168.10.0/24
    python main.py --cidr 192.168.10.37 255.255.255.0
    python main.py --vlsm 192.168.0.0/24 "A=100, B=50, C=25, D=10"

Uso interactivo (con menú):
    python main.py --consola
"""

from __future__ import annotations

from calculadora_ip import ErrorEntrada, calcular_cidr_desde_texto, calcular_vlsm
from calculadora_ip.vlsm import leer_requerimientos


# ---------------------------------------------------------------------------
# Formato de salida
# ---------------------------------------------------------------------------
def formatear_cidr(r) -> str:
    """Devuelve el resultado CIDR como texto alineado en dos columnas."""
    filas = [
        ("Dirección IP", r.ip),
        ("Clase / tipo", f"{r.clase} / {r.tipo}"),
        ("Red", r.red_cidr),
        ("Máscara", f"{r.mascara}  (/{r.prefijo})"),
        ("Wildcard", r.wildcard),
        ("Broadcast", r.broadcast),
        ("Primer host", r.primer_host),
        ("Último host", r.ultimo_host),
        ("Total de direcciones", f"{r.total_direcciones:,}"),
        ("Hosts válidos", f"{r.hosts_validos:,}"),
    ]
    lineas = ["", "=== Calculadora IP (CIDR) ==="]
    lineas += [f"  {campo:<22}{valor}" for campo, valor in filas]
    if r.nota:
        lineas.append(f"  Nota: {r.nota}")
    lineas.append("")
    lineas.append("  Representación binaria ( | separa red de host )")
    lineas += [f"  {campo:<12}{bits}" for campo, bits in r.binario.items()]
    return "\n".join(lineas)


def formatear_vlsm(r) -> str:
    """Devuelve la asignación VLSM como tabla de texto."""
    encabezados = ["Subred", "Pedidos", "Válidos", "Desperd.", "Red", "Máscara",
                   "Primer host", "Último host", "Broadcast"]
    filas = [[s.nombre, s.hosts_solicitados, s.hosts_validos, s.desperdicio, s.red_cidr,
              s.mascara, s.primer_host, s.ultimo_host, s.broadcast] for s in r.subredes]
    anchos = [max(len(str(x)) for x in col) for col in zip(encabezados, *filas)]

    def linea(valores):
        return "  " + "  ".join(str(v).ljust(a) for v, a in zip(valores, anchos))

    salida = ["", f"=== Calculadora VLSM: red base {r.red_base}/{r.prefijo_base} ===", linea(encabezados),
              "  " + "  ".join("-" * a for a in anchos)]
    salida += [linea(f) for f in filas]
    salida.append("")
    salida.append(f"  Direcciones usadas : {r.direcciones_usadas:,} de {r.direcciones_totales:,} "
                  f"({r.porcentaje_usado:.2f} %)")
    salida.append(f"  Direcciones libres : {r.direcciones_libres:,}"
                  + (f"  (desde {r.siguiente_libre})" if r.siguiente_libre else ""))
    salida.append(f"  Hosts desperdiciados dentro de las subredes: {r.desperdicio_total:,}")
    salida += [f"  Aviso: {a}" for a in r.avisos]
    return "\n".join(salida)


# ---------------------------------------------------------------------------
# Modo directo y modo interactivo
# ---------------------------------------------------------------------------
def ejecutar_argumentos(argumentos: list[str]) -> int:
    """Atiende --cidr y --vlsm. Devuelve el código de salida del programa."""
    try:
        if argumentos[0] == "--cidr" and len(argumentos) >= 2:
            print(formatear_cidr(calcular_cidr_desde_texto(" ".join(argumentos[1:]))))
            return 0
        if argumentos[0] == "--vlsm" and len(argumentos) >= 3:
            print(formatear_vlsm(calcular_vlsm(argumentos[1], leer_requerimientos(",".join(argumentos[2:])))))
            return 0
    except ErrorEntrada as error:
        print(f"Error: {error}")
        return 1
    print(__doc__)
    return 2


def menu_interactivo() -> None:
    """Menú de texto para usar ambas calculadoras sin interfaz gráfica."""
    while True:
        print("\n===== CALCULADORA IP =====")
        print("  1) Calculadora IP (CIDR)")
        print("  2) Calculadora VLSM")
        print("  0) Salir")
        opcion = input("Elige una opción: ").strip()

        try:
            if opcion == "1":
                texto = input("IP con prefijo o máscara (ej. 192.168.10.0/24): ")
                print(formatear_cidr(calcular_cidr_desde_texto(texto)))
            elif opcion == "2":
                base = input("Red base (ej. 192.168.0.0/24): ")
                reqs = input("Subredes como Nombre=hosts separadas por comas (ej. A=100, B=50): ")
                print(formatear_vlsm(calcular_vlsm(base, leer_requerimientos(reqs))))
            elif opcion == "0":
                return
            else:
                print("Opción no válida.")
        except ErrorEntrada as error:
            print(f"Error: {error}")
