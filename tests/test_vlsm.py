"""Pruebas de la Calculadora VLSM."""

import unittest

from calculadora_ip import ErrorEntrada, Requerimiento, calcular_vlsm
from calculadora_ip.conversiones import ip_a_entero
from calculadora_ip.vlsm import bits_de_host_para, leer_requerimientos


def reqs(**pares):
    return [Requerimiento(nombre, hosts) for nombre, hosts in pares.items()]


class PruebasVLSM(unittest.TestCase):

    def test_bits_de_host(self):
        # needed = hosts + 2 ; bits = ceil(log2(needed))
        self.assertEqual(bits_de_host_para(2), 2)      # 4 direcciones  -> /30
        self.assertEqual(bits_de_host_para(14), 4)     # 16 exactas     -> /28
        self.assertEqual(bits_de_host_para(15), 5)     # 17 -> 32       -> /27
        self.assertEqual(bits_de_host_para(100), 7)    # 102 -> 128     -> /25
        self.assertEqual(bits_de_host_para(120), 7)    # ejemplo de la guía -> /25
        self.assertEqual(bits_de_host_para(8000), 13)  # 8002 -> 8192   -> /19

    def test_caso_de_la_guia(self):
        """Base 192.168.0.0/24 con A=100, B=50, C=25, D=10."""
        r = calcular_vlsm("192.168.0.0/24", reqs(A=100, B=50, C=25, D=10))
        obtenido = [(s.nombre, s.red_cidr, s.broadcast, s.hosts_validos, s.desperdicio) for s in r.subredes]
        self.assertEqual(obtenido, [
            ("A", "192.168.0.0/25", "192.168.0.127", 126, 26),
            ("B", "192.168.0.128/26", "192.168.0.191", 62, 12),
            ("C", "192.168.0.192/27", "192.168.0.223", 30, 5),
            ("D", "192.168.0.224/28", "192.168.0.239", 14, 4),
        ])
        self.assertEqual(r.direcciones_usadas, 240)
        self.assertEqual(r.direcciones_libres, 16)
        self.assertEqual(r.siguiente_libre, "192.168.0.240")

    def test_tarea_vlsm_148_204(self):
        """Ejercicio VLSM de clase: 148.204.0.0/16 con 3 VLAN y 3 enlaces."""
        r = calcular_vlsm("148.204.0.0/16", reqs(VLAN1=8000, VLAN2=1000, VLAN3=200,
                                                   Enlace1=2, Enlace2=2, Enlace3=2))
        self.assertEqual([s.red_cidr for s in r.subredes], [
            "148.204.0.0/19", "148.204.32.0/22", "148.204.36.0/24",
            "148.204.37.0/30", "148.204.37.4/30", "148.204.37.8/30",
        ])
        self.assertEqual(r.subredes[0].broadcast, "148.204.31.255")
        self.assertEqual(r.direcciones_usadas, 9484)
        self.assertEqual(r.direcciones_libres, 56052)
        self.assertEqual(r.siguiente_libre, "148.204.37.12")

    def test_orden_de_entrada_no_importa(self):
        a = calcular_vlsm("10.0.0.0/24", reqs(D=10, A=100, C=25, B=50))
        self.assertEqual([s.nombre for s in a.subredes], ["A", "B", "C", "D"])

    def test_sin_solapamientos_y_alineados(self):
        r = calcular_vlsm("10.0.0.0/16", reqs(a=500, b=3000, c=60, d=2, e=1000, f=7, g=250))
        anterior_fin = None
        for s in r.subredes:
            inicio, fin = ip_a_entero(s.red), ip_a_entero(s.broadcast)
            self.assertEqual(inicio % s.tamano_bloque, 0, "el bloque debe estar alineado a su tamaño")
            self.assertGreaterEqual(s.hosts_validos, s.hosts_solicitados)
            if anterior_fin is not None:
                self.assertEqual(inicio, anterior_fin + 1, "las subredes deben quedar contiguas")
            anterior_fin = fin

    def test_red_base_no_normalizada_genera_aviso(self):
        r = calcular_vlsm("192.168.0.77/24", reqs(A=10))
        self.assertEqual(r.red_base, "192.168.0.0")
        self.assertTrue(r.avisos)

    def test_espacio_insuficiente(self):
        """Caso límite de la guía: pedir más hosts de los disponibles."""
        with self.assertRaises(ErrorEntrada) as ctx:
            calcular_vlsm("192.168.0.0/24", reqs(A=300))
        self.assertIn("insuficiente", str(ctx.exception))
        with self.assertRaises(ErrorEntrada):
            calcular_vlsm("192.168.0.0/24", reqs(A=126, B=126, C=2))   # 128+128+4 > 256

    def test_llena_la_red_exactamente(self):
        r = calcular_vlsm("192.168.0.0/24", reqs(A=126, B=126))
        self.assertEqual(r.direcciones_libres, 0)
        self.assertEqual(r.siguiente_libre, "")

    def test_requerimientos_invalidos(self):
        for lista in ([], reqs(A=0), reqs(A=-5), [Requerimiento("A", "diez")],
                      [Requerimiento("A", 10), Requerimiento("a", 5)]):
            with self.subTest(lista=lista):
                with self.assertRaises(ErrorEntrada):
                    calcular_vlsm("192.168.0.0/24", lista)

    def test_leer_requerimientos_texto(self):
        lista = leer_requerimientos("Ventas=100, RH:50; Enlace=2")
        self.assertEqual([(r.nombre, int(r.hosts)) for r in lista], [("Ventas", 100), ("RH", 50), ("Enlace", 2)])


if __name__ == "__main__":
    unittest.main()
