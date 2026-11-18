"""
errores.py
----------
Excepción propia del proyecto. Todas las validaciones lanzan ErrorEntrada con
un mensaje en español pensado para mostrarse directamente al usuario, tanto en
la interfaz gráfica como en la consola.
"""


class ErrorEntrada(ValueError):
    """Error causado por un dato mal escrito o por una red sin espacio suficiente."""
