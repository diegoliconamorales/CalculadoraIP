# Calculadora IP — CIDR y VLSM

Proyecto 2 de **Redes de Computadoras** (ESCOM-IPN, grupo 5CM3).
Aplicación de escritorio en Python con dos herramientas:

1. **Calculadora IP (CIDR):** a partir de una IP y su prefijo o máscara obtiene la
   red, el broadcast, el rango de hosts, la máscara y wildcard, los hosts válidos, la
   clase, el tipo de dirección y la representación binaria.
2. **Calculadora VLSM:** a partir de una red base y una lista de subredes con los
   hosts que necesita cada una, asigna bloques contiguos de mayor a menor, sin
   traslapes, e indica el espacio desperdiciado y el espacio libre.

---

## 1. Ejecutar sin instalar nada (ejecutables)

Los programas listos para Windows están en la sección [Releases](https://github.com/diegoliconamorales/CalculadoraIP/releases) de este repositorio (y en la carpeta `ejecutables/` del ZIP entregado):

| Archivo | Qué abre |
|---|---|
| `CalculadoraIP.exe` | Ambas calculadoras, en pestañas |
| `CalculadoraCIDR.exe` | Solo la Calculadora IP (CIDR) |
| `CalculadoraVLSM.exe` | Solo la Calculadora VLSM |

Doble clic sobre cualquiera de ellos. Si Windows SmartScreen muestra un aviso,
elegir **Más información → Ejecutar de todas formas** (el programa no está firmado
digitalmente).

## 2. Ejecutar desde el código fuente

**Requisito:** Python 3.10 o superior. En Windows, al instalarlo marcar
*"Add python.exe to PATH"*. No se necesita instalar ninguna biblioteca adicional:
solo se usa la biblioteca estándar (Tkinter viene incluido en el instalador de Windows).

| Sistema | Interfaz gráfica | Modo consola |
|---|---|---|
| Windows | doble clic en `ejecutar.bat` | doble clic en `ejecutar_consola.bat` |
| Linux / macOS | `./ejecutar.sh` | `./ejecutar.sh --consola` |
| Cualquiera | `python main.py` | `python main.py --consola` |

Para abrir solo una de las calculadoras: `python calculadora_cidr.py` o
`python calculadora_vlsm.py`.

En Linux, si aparece `No module named tkinter`, instalarlo con
`sudo apt install python3-tk`. Mientras tanto el programa se abre en modo consola.

### Cálculos directos desde la terminal

```
python main.py --cidr 192.168.10.0/24
python main.py --cidr 10.100.83.139 255.255.224.0
python main.py --vlsm 192.168.0.0/24 "A=100, B=50, C=25, D=10"
```

## 3. Cómo se usa

**CIDR.** Escribir la IP y, en el segundo campo, el prefijo (`/24` o `24`) o la
máscara (`255.255.255.0`). También se puede escribir todo en el primer campo
(`192.168.10.0/24`). Presionar **Calcular** o Enter. El botón **Ejemplo** carga
el caso de prueba de la guía.

**VLSM.** Escribir la red base (`192.168.0.0/24`), luego el nombre y los hosts
de cada subred y presionar **Agregar** (o Enter). Al terminar la lista, presionar
**Calcular VLSM**. El botón **Cargar ejemplo** carga el caso A=100, B=50, C=25, D=10.

En ambas pestañas, **Copiar resultados** copia la tabla como texto.

## 4. Pruebas

```
python -m unittest discover -s tests -t . -v
```

En Windows: doble clic en `ejecutar_pruebas.bat`. Son 24 pruebas que cubren:

| Caso | Resultado esperado |
|---|---|
| CIDR `192.168.10.0/24` | red .0, hosts .1 – .254, broadcast .255 |
| CIDR `10.100.83.139` + `255.255.224.0` | red 10.100.64.0/19, 8 190 hosts |
| VLSM `192.168.0.0/24`: A=100, B=50, C=25, D=10 | /25, /26, /27, /28 contiguas; 16 direcciones libres |
| VLSM `148.204.0.0/16`: 8000, 1000, 200, 3 × 2 | /19, /22, /24, 3 × /30; libre desde 148.204.37.12 |
| VLSM `192.168.0.0/24` con A=300 | Error: espacio insuficiente |
| Entradas inválidas (`300.1.1.1`, `/33`, `255.0.255.0`, hosts = 0, nombres repetidos) | Mensaje de error claro |

## 5. Generar los ejecutables (.exe)

En Windows, doble clic en `construir_exe.bat`. El script instala PyInstaller,
corre las pruebas y crea los tres `.exe` en la carpeta `dist/`.

Comando manual equivalente:

```
py -m pip install pyinstaller
py -m PyInstaller --onefile --windowed --name CalculadoraIP main.py
```

## 6. Estructura del proyecto

```
CalculadoraIP/
├── main.py                  Punto de entrada (interfaz gráfica o consola)
├── calculadora_cidr.py      Abre solo la Calculadora CIDR
├── calculadora_vlsm.py      Abre solo la Calculadora VLSM
├── calculadora_ip/          LÓGICA (sin interfaz)
│   ├── conversiones.py      IP <-> entero de 32 bits, máscaras, binario, clase
│   ├── cidr.py              Cálculo CIDR
│   ├── vlsm.py              Algoritmo VLSM
│   └── errores.py           Excepción ErrorEntrada
├── interfaz/                PRESENTACIÓN
│   ├── gui.py               Ventana Tkinter
│   └── consola.py           Menú y salida en texto
├── tests/                   Pruebas unitarias (unittest)
├── ejecutar.bat / ejecutar_consola.bat / ejecutar_pruebas.bat / ejecutar.sh
├── construir_exe.bat        Genera los .exe con PyInstaller
└── requirements.txt
```

## 7. Bibliotecas y licencias

- **Python** y su biblioteca estándar (`tkinter`, `unittest`, `dataclasses`):
  Python Software Foundation License.
- **PyInstaller** (solo para generar los ejecutables): GPL 2.0 con excepción que
  permite distribuir los programas generados.
- Los cálculos de red no usan bibliotecas externas ni el módulo `ipaddress`:
  la conversión IP ↔ entero y las operaciones de bits están implementadas en
  `calculadora_ip/conversiones.py`.
