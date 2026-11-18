"""
main.py
-------
Punto de entrada de la Calculadora IP (CIDR y VLSM).

    python main.py                      -> ventana con ambas calculadoras
    python main.py --consola            -> menú de texto
    python main.py --cidr 10.0.0.0/8    -> cálculo CIDR directo en consola
    python main.py --vlsm 192.168.0.0/24 "A=100, B=50"  -> cálculo VLSM directo
"""

import sys


def iniciar_interfaz(modo: str = "ambas") -> None:
    """
    Abre la ventana gráfica. Si el equipo no tiene Tkinter o entorno gráfico,
    se usa el menú de consola para que el programa nunca deje de funcionar.
    """
    try:
        from interfaz.gui import iniciar
        iniciar(modo)
    except Exception as error:  # Tkinter ausente o sin pantalla disponible
        print(f"No se pudo abrir la interfaz gráfica ({error}). Se usará el modo consola.")
        from interfaz.consola import menu_interactivo
        menu_interactivo()


def main(argumentos: list[str]) -> int:
    if argumentos and argumentos[0] == "--consola":
        from interfaz.consola import menu_interactivo
        menu_interactivo()
        return 0
    if argumentos and argumentos[0] in ("--cidr", "--vlsm", "--ayuda", "-h", "--help"):
        from interfaz.consola import ejecutar_argumentos
        return ejecutar_argumentos(argumentos)
    iniciar_interfaz("ambas")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
