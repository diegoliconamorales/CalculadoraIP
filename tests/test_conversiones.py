"""Pruebas de las conversiones básicas (IP <-> entero, máscaras, binario)."""

import unittest

from calculadora_ip.conversiones import (
    a_binario, clase_de_ip, entero_a_ip, interpretar_red, ip_a_entero,
    leer_prefijo_o_mascara, mascara_a_prefijo, prefijo_a_mascara, tipo_de_ip,
)
from calculadora_ip.errores import ErrorEntrada


class PruebasConversion(unittest.TestCase):

    def test_ip_a_entero_y_regreso(self):
        self.assertEqual(ip_a_entero("192.168.1.10"), 3232235786)
        self.assertEqual(ip_a_entero("0.0.0.0"), 0)
        self.assertEqual(ip_a_entero("255.255.255.255"), 0xFFFFFFFF)
        for ip in ("10.0.0.1", "148.204.37.11", "172.16.66.0"):
            self.assertEqual(entero_a_ip(ip_a_entero(ip)), ip)

    def test_ip_invalidas(self):
        for mala in ("", "192.168.1", "192.168.1.1.1", "300.1.1.1", "a.b.c.d", "192.168.-1.1", "1..2.3"):
            with self.subTest(ip=mala):
                with self.assertRaises(ErrorEntrada):
                    ip_a_entero(mala)

    def test_prefijo_a_mascara(self):
        casos = {0: "0.0.0.0", 8: "255.0.0.0", 19: "255.255.224.0", 22: "255.255.252.0",
                 24: "255.255.255.0", 27: "255.255.255.224", 30: "255.255.255.252", 32: "255.255.255.255"}
        for prefijo, mascara in casos.items():
            with self.subTest(prefijo=prefijo):
                self.assertEqual(entero_a_ip(prefijo_a_mascara(prefijo)), mascara)
                self.assertEqual(mascara_a_prefijo(mascara), prefijo)

    def test_mascara_no_contigua(self):
        for mala in ("255.0.255.0", "255.255.255.1", "0.255.255.255", "255.255.253.0"):
            with self.subTest(mascara=mala):
                with self.assertRaises(ErrorEntrada):
                    mascara_a_prefijo(mala)

    def test_prefijo_fuera_de_rango(self):
        for malo in ("/33", "40", "/-1", "veinte"):
            with self.subTest(prefijo=malo):
                with self.assertRaises(ErrorEntrada):
                    leer_prefijo_o_mascara(malo)

    def test_formas_de_entrada(self):
        esperado = (ip_a_entero("192.168.1.10"), 24)
        self.assertEqual(interpretar_red("192.168.1.10/24"), esperado)
        self.assertEqual(interpretar_red("192.168.1.10/255.255.255.0"), esperado)
        self.assertEqual(interpretar_red("192.168.1.10 255.255.255.0"), esperado)
        self.assertEqual(interpretar_red("192.168.1.10", "/24"), esperado)
        self.assertEqual(interpretar_red("192.168.1.10", "255.255.255.0"), esperado)
        with self.assertRaises(ErrorEntrada):
            interpretar_red("192.168.1.10")          # falta el prefijo
        with self.assertRaises(ErrorEntrada):
            interpretar_red("192.168.1.10/24", "/24")  # prefijo duplicado

    def test_binario(self):
        self.assertEqual(a_binario(ip_a_entero("255.255.255.0")),
                         "11111111.11111111.11111111.00000000")
        self.assertEqual(a_binario(ip_a_entero("192.168.1.10"), 26),
                         "11000000.10101000.00000001.00|001010")

    def test_clase_y_tipo(self):
        self.assertEqual(clase_de_ip(ip_a_entero("10.25.66.154")), "A")
        self.assertEqual(clase_de_ip(ip_a_entero("172.31.254.12")), "B")
        self.assertEqual(clase_de_ip(ip_a_entero("208.100.54.209")), "C")
        self.assertEqual(tipo_de_ip(ip_a_entero("192.168.0.1")), "Privada (RFC 1918)")
        self.assertEqual(tipo_de_ip(ip_a_entero("172.20.0.1")), "Privada (RFC 1918)")
        self.assertEqual(tipo_de_ip(ip_a_entero("148.204.0.1")), "Pública")


if __name__ == "__main__":
    unittest.main()
