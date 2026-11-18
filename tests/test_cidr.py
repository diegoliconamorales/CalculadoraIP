"""Pruebas de la Calculadora IP (CIDR)."""

import unittest

from calculadora_ip import ErrorEntrada, calcular_cidr_desde_texto


class PruebasCIDR(unittest.TestCase):

    def test_caso_de_la_guia(self):
        """Caso sugerido: 192.168.10.0/24."""
        r = calcular_cidr_desde_texto("192.168.10.0/24")
        self.assertEqual(r.red, "192.168.10.0")
        self.assertEqual(r.primer_host, "192.168.10.1")
        self.assertEqual(r.ultimo_host, "192.168.10.254")
        self.assertEqual(r.broadcast, "192.168.10.255")
        self.assertEqual(r.mascara, "255.255.255.0")
        self.assertEqual(r.wildcard, "0.0.0.255")
        self.assertEqual(r.hosts_validos, 254)

    def test_ip_con_mascara_red_wifi_ipn(self):
        """IP + máscara decimal: 10.100.83.139 255.255.224.0 (/19)."""
        r = calcular_cidr_desde_texto("10.100.83.139", "255.255.224.0")
        self.assertEqual(r.prefijo, 19)
        self.assertEqual(r.red, "10.100.64.0")
        self.assertEqual(r.primer_host, "10.100.64.1")
        self.assertEqual(r.ultimo_host, "10.100.95.254")
        self.assertEqual(r.broadcast, "10.100.95.255")
        self.assertEqual(r.hosts_validos, 8190)

    def test_ejercicios_de_subneteo(self):
        """Ejercicio 1 de la Tarea 14: subred y broadcast de varias IP."""
        casos = [
            ("192.168.100.25/30", "192.168.100.24", "192.168.100.27"),
            ("192.168.100.37/28", "192.168.100.32", "192.168.100.47"),
            ("192.168.100.66/27", "192.168.100.64", "192.168.100.95"),
            ("192.168.100.17/29", "192.168.100.16", "192.168.100.23"),
            ("192.168.100.99/26", "192.168.100.64", "192.168.100.127"),
            ("192.168.100.99/25", "192.168.100.0", "192.168.100.127"),
            ("10.16.3.65/23", "10.16.2.0", "10.16.3.255"),
            ("172.16.66.0/21", "172.16.64.0", "172.16.71.255"),
        ]
        for entrada, red, broadcast in casos:
            with self.subTest(entrada=entrada):
                r = calcular_cidr_desde_texto(entrada)
                self.assertEqual(r.red, red)
                self.assertEqual(r.broadcast, broadcast)

    def test_casos_especiales_31_y_32(self):
        r31 = calcular_cidr_desde_texto("10.0.0.0/31")
        self.assertEqual(r31.hosts_validos, 2)
        self.assertEqual((r31.primer_host, r31.ultimo_host), ("10.0.0.0", "10.0.0.1"))
        r32 = calcular_cidr_desde_texto("10.0.0.5/32")
        self.assertEqual(r32.hosts_validos, 1)
        self.assertEqual(r32.red, "10.0.0.5")

    def test_binario_incluido(self):
        r = calcular_cidr_desde_texto("192.168.10.0/24")
        self.assertEqual(r.binario["Máscara"], "11111111.11111111.11111111|00000000")

    def test_entradas_invalidas(self):
        for mala in ("", "abc", "192.168.1.0/33", "300.1.1.1/24", "192.168.1.0"):
            with self.subTest(entrada=mala):
                with self.assertRaises(ErrorEntrada):
                    calcular_cidr_desde_texto(mala)
        with self.assertRaises(ErrorEntrada):
            calcular_cidr_desde_texto("192.168.1.1", "255.0.255.0")


if __name__ == "__main__":
    unittest.main()
