"""
gui.py
------
Interfaz gráfica (Tkinter) de la Calculadora IP.

La ventana solo se encarga de LEER los datos y MOSTRAR resultados; todos los
cálculos los hace el paquete calculadora_ip. Así la lógica puede probarse por
separado (carpeta tests/) y reutilizarse en la versión de consola.

Se puede abrir en tres modos:
    App("ambas")  -> pestañas CIDR y VLSM
    App("cidr")   -> solo la Calculadora IP (CIDR)
    App("vlsm")   -> solo la Calculadora VLSM
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from calculadora_ip import ErrorEntrada, Requerimiento, calcular_cidr_desde_texto, calcular_vlsm
from interfaz.consola import formatear_cidr, formatear_vlsm

# Colores de la interfaz (guinda IPN)
COLOR_PRINCIPAL = "#6C1D45"
COLOR_FONDO = "#F4F1F3"
COLOR_TEXTO_SUAVE = "#5A5A5A"
FUENTE = ("Segoe UI", 10)
FUENTE_MONO = ("Consolas", 10)


def configurar_estilos(raiz: tk.Tk) -> None:
    """Define la apariencia de los widgets ttk."""
    estilo = ttk.Style(raiz)
    if "clam" in estilo.theme_names():
        estilo.theme_use("clam")
    raiz.configure(background=COLOR_FONDO)
    estilo.configure(".", font=FUENTE, background=COLOR_FONDO)
    estilo.configure("TFrame", background=COLOR_FONDO)
    estilo.configure("TLabelframe", background=COLOR_FONDO)
    estilo.configure("TLabelframe.Label", background=COLOR_FONDO, foreground=COLOR_PRINCIPAL,
                     font=("Segoe UI", 10, "bold"))
    estilo.configure("TLabel", background=COLOR_FONDO)
    estilo.configure("Titulo.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_PRINCIPAL)
    estilo.configure("Sub.TLabel", foreground=COLOR_TEXTO_SUAVE)
    estilo.configure("Resumen.TLabel", font=("Segoe UI", 10, "bold"))
    estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"), foreground="white",
                     background=COLOR_PRINCIPAL, padding=(14, 6))
    estilo.map("Accion.TButton", background=[("active", "#8E2A5D")])
    estilo.configure("TButton", padding=(10, 5))
    # El alto de fila se calcula con la letra real, así no se encima el texto
    # cuando Windows usa escalado de pantalla (125 %, 150 %...).
    alto_fila = tkfont.Font(root=raiz, font=FUENTE_MONO).metrics("linespace") + 8
    estilo.configure("Treeview", rowheight=alto_fila, font=FUENTE)
    estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                     background="#E4D3DC", foreground="#3A0F25")
    estilo.configure("TNotebook.Tab", padding=(18, 6), font=("Segoe UI", 10, "bold"))


def tabla_con_scroll(padre, columnas: dict[str, tuple[str, int]], alto: int,
                     expandir: bool = True) -> ttk.Treeview:
    """
    Crea un Treeview con barras de desplazamiento.
    columnas = {"id": ("Encabezado", ancho_en_pixeles)}
    expandir = False mantiene la tabla con su alto fijo (no crece con la ventana).
    """
    marco = ttk.Frame(padre)
    marco.pack(fill="both" if expandir else "x", expand=expandir, padx=8, pady=8)
    tabla = ttk.Treeview(marco, columns=list(columnas), show="headings", height=alto)
    for clave, (titulo, ancho) in columnas.items():
        tabla.heading(clave, text=titulo)
        tabla.column(clave, width=ancho, minwidth=60, anchor="center", stretch=True)
    barra_v = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    barra_h = ttk.Scrollbar(marco, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)
    tabla.grid(row=0, column=0, sticky="nsew")
    barra_v.grid(row=0, column=1, sticky="ns")
    barra_h.grid(row=1, column=0, sticky="ew")
    marco.rowconfigure(0, weight=1)
    marco.columnconfigure(0, weight=1)
    tabla.tag_configure("par", background="#FFFFFF")
    tabla.tag_configure("impar", background="#F7EFF3")
    return tabla


def vaciar(tabla: ttk.Treeview) -> None:
    tabla.delete(*tabla.get_children())


# ===========================================================================
# Calculadora IP (CIDR)
# ===========================================================================
class PanelCIDR(ttk.Frame):
    """Pestaña de la Calculadora IP (CIDR)."""

    def __init__(self, padre):
        super().__init__(padre, padding=12)
        self.ultimo_resultado = None

        ttk.Label(self, text="Calculadora IP (CIDR)", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text="Escribe una dirección IP y su prefijo (/24) o máscara (255.255.255.0). "
                             "También puedes escribir todo junto: 192.168.10.0/24",
                  style="Sub.TLabel").pack(anchor="w", pady=(0, 8))

        # --- Entradas -------------------------------------------------------
        entradas = ttk.LabelFrame(self, text="Datos de entrada", padding=10)
        entradas.pack(fill="x")

        ttk.Label(entradas, text="Dirección IP:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.ent_ip = ttk.Entry(entradas, width=24)
        self.ent_ip.grid(row=0, column=1, padx=(0, 16))

        ttk.Label(entradas, text="Prefijo o máscara:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.ent_mascara = ttk.Combobox(entradas, width=18,
                                        values=[f"/{n}" for n in range(8, 33)])
        self.ent_mascara.grid(row=0, column=3, padx=(0, 16))

        ttk.Button(entradas, text="Calcular", style="Accion.TButton",
                   command=self.calcular).grid(row=0, column=4, padx=4)
        ttk.Button(entradas, text="Ejemplo", command=self.cargar_ejemplo).grid(row=0, column=5, padx=4)
        ttk.Button(entradas, text="Limpiar", command=self.limpiar).grid(row=0, column=6, padx=4)

        for widget in (self.ent_ip, self.ent_mascara):
            widget.bind("<Return>", lambda _evento: self.calcular())

        # El botón de copiar se empaqueta PRIMERO (abajo) para que siempre sea visible.
        acciones = ttk.Frame(self)
        acciones.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Button(acciones, text="Copiar resultados", command=self.copiar).pack(side="right")

        # Resultados y binario van LADO A LADO: así cada tabla tiene toda la
        # altura disponible y no se corta ninguna fila aunque Windows use escalado.
        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True, pady=(10, 0))
        cuerpo.columnconfigure(0, weight=5, uniform="mitades")
        cuerpo.columnconfigure(1, weight=6, uniform="mitades")
        cuerpo.rowconfigure(0, weight=1)

        # --- Resultados -----------------------------------------------------
        resultados = ttk.LabelFrame(cuerpo, text="Resultados", padding=4)
        resultados.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.lbl_nota = ttk.Label(resultados, text="", foreground=COLOR_PRINCIPAL, wraplength=480)
        self.lbl_nota.pack(side="bottom", anchor="w", padx=10, pady=(0, 4))
        self.tabla = tabla_con_scroll(resultados, {"campo": ("Dato", 170), "valor": ("Valor", 300)}, 9)
        self.tabla.column("campo", anchor="w")
        self.tabla.column("valor", anchor="w")

        # --- Binario --------------------------------------------------------
        binario = ttk.LabelFrame(cuerpo, text="Representación binaria  ( | separa red de host )", padding=4)
        binario.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.tabla_bin = tabla_con_scroll(binario, {"campo": ("Dato", 110), "bits": ("Binario", 380)}, 5)
        self.tabla_bin.column("campo", anchor="w")
        self.tabla_bin.column("bits", anchor="w")
        self.tabla_bin.tag_configure("mono", font=FUENTE_MONO)

        self.ent_ip.focus_set()

    # --- Acciones ----------------------------------------------------------
    def calcular(self) -> None:
        try:
            resultado = calcular_cidr_desde_texto(self.ent_ip.get(), self.ent_mascara.get())
        except ErrorEntrada as error:
            messagebox.showerror("Dato no válido", str(error), parent=self)
            return
        self.ultimo_resultado = resultado
        self.mostrar(resultado)

    def mostrar(self, r) -> None:
        vaciar(self.tabla)
        filas = [
            ("Dirección IP", r.ip),
            ("Clase / tipo", f"{r.clase}  /  {r.tipo}"),
            ("Dirección de red", r.red_cidr),
            ("Máscara", f"{r.mascara}   (/{r.prefijo})"),
            ("Wildcard", r.wildcard),
            ("Broadcast", r.broadcast),
            ("Rango de hosts", r.rango_hosts),
            ("Total de direcciones", f"{r.total_direcciones:,}"),
            ("Hosts válidos", f"{r.hosts_validos:,}"),
        ]
        for i, (campo, valor) in enumerate(filas):
            self.tabla.insert("", "end", values=(campo, valor), tags=("par" if i % 2 == 0 else "impar",))
        self.lbl_nota.configure(text=f"Nota: {r.nota}" if r.nota else "")

        vaciar(self.tabla_bin)
        for campo, bits in r.binario.items():
            self.tabla_bin.insert("", "end", values=(campo, bits), tags=("mono",))

    def cargar_ejemplo(self) -> None:
        self.limpiar()
        self.ent_ip.insert(0, "192.168.10.0")
        self.ent_mascara.set("/24")
        self.calcular()

    def limpiar(self) -> None:
        self.ent_ip.delete(0, "end")
        self.ent_mascara.set("")
        vaciar(self.tabla)
        vaciar(self.tabla_bin)
        self.lbl_nota.configure(text="")
        self.ultimo_resultado = None
        self.ent_ip.focus_set()

    def copiar(self) -> None:
        if self.ultimo_resultado is None:
            messagebox.showinfo("Sin resultados", "Primero realiza un cálculo.", parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(formatear_cidr(self.ultimo_resultado))
        messagebox.showinfo("Copiado", "Los resultados se copiaron al portapapeles.", parent=self)


# ===========================================================================
# Calculadora VLSM
# ===========================================================================
class PanelVLSM(ttk.Frame):
    """Pestaña de la Calculadora VLSM."""

    EJEMPLO_BASE = "192.168.0.0/24"
    EJEMPLO_SUBREDES = [("A", 100), ("B", 50), ("C", 25), ("D", 10)]

    def __init__(self, padre):
        super().__init__(padre, padding=12)
        self.ultimo_resultado = None

        ttk.Label(self, text="Calculadora VLSM", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text="Escribe la red base, agrega cada subred con los hosts que necesita y "
                             "presiona Calcular VLSM.", style="Sub.TLabel").pack(anchor="w", pady=(0, 8))

        superior = ttk.Frame(self)
        superior.pack(fill="x")

        # --- Red base y requerimientos -------------------------------------
        datos = ttk.LabelFrame(superior, text="Red base y subredes requeridas", padding=10)
        datos.pack(side="left", fill="both", expand=True)

        ttk.Label(datos, text="Red base:").grid(row=0, column=0, sticky="w")
        self.ent_base = ttk.Entry(datos, width=22)
        self.ent_base.grid(row=0, column=1, sticky="w", padx=6, pady=(0, 8))
        ttk.Label(datos, text="ej. 10.0.0.0/16", style="Sub.TLabel").grid(row=0, column=2, sticky="w")

        ttk.Label(datos, text="Nombre:").grid(row=1, column=0, sticky="w")
        self.ent_nombre = ttk.Entry(datos, width=22)
        self.ent_nombre.grid(row=1, column=1, sticky="w", padx=6)
        ttk.Label(datos, text="Hosts:").grid(row=1, column=2, sticky="w")
        self.ent_hosts = ttk.Entry(datos, width=10)
        self.ent_hosts.grid(row=1, column=3, sticky="w", padx=6)
        ttk.Button(datos, text="Agregar", command=self.agregar).grid(row=1, column=4, padx=4)
        self.ent_hosts.bind("<Return>", lambda _e: self.agregar())
        self.ent_nombre.bind("<Return>", lambda _e: self.ent_hosts.focus_set())

        botones = ttk.Frame(datos)
        botones.grid(row=2, column=0, columnspan=5, sticky="w", pady=(8, 0))
        ttk.Button(botones, text="Quitar seleccionada", command=self.quitar).pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Vaciar lista", command=self.vaciar_lista).pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Cargar ejemplo", command=self.cargar_ejemplo).pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Calcular VLSM", style="Accion.TButton",
                   command=self.calcular).pack(side="left", padx=(12, 0))

        lista = ttk.LabelFrame(superior, text="Subredes solicitadas", padding=4)
        lista.pack(side="left", fill="both", padx=(10, 0))
        self.tabla_req = tabla_con_scroll(lista, {"nombre": ("Nombre", 160), "hosts": ("Hosts", 90)}, 5)

        # El resumen se empaqueta primero (abajo) para que siempre sea visible.
        inferior = ttk.Frame(self)
        inferior.pack(side="bottom", fill="x", pady=(8, 0))
        self.lbl_resumen = ttk.Label(inferior, text="", style="Resumen.TLabel", wraplength=850)
        self.lbl_resumen.pack(side="left")
        ttk.Button(inferior, text="Copiar resultados", command=self.copiar).pack(side="right")

        # --- Resultados -----------------------------------------------------
        resultados = ttk.LabelFrame(self, text="Asignación VLSM (de mayor a menor)", padding=4)
        resultados.pack(fill="both", expand=True, pady=(10, 0))
        columnas = {
            "nombre": ("Subred", 110), "pedidos": ("Hosts pedidos", 100), "validos": ("Hosts válidos", 100),
            "desperdicio": ("Desperdicio", 90), "red": ("Red / prefijo", 140), "mascara": ("Máscara", 130),
            "primer": ("Primer host", 120), "ultimo": ("Último host", 120), "broadcast": ("Broadcast", 120),
        }
        self.tabla_out = tabla_con_scroll(resultados, columnas, 8)

        self.ent_base.focus_set()

    # --- Lista de requerimientos ------------------------------------------
    def agregar(self) -> None:
        nombre = self.ent_nombre.get().strip() or f"Subred {len(self.tabla_req.get_children()) + 1}"
        hosts = self.ent_hosts.get().strip()
        if not hosts.isdigit() or int(hosts) < 1:
            messagebox.showerror("Dato no válido",
                                 "Los hosts deben ser un número entero mayor que 0.", parent=self)
            self.ent_hosts.focus_set()
            return
        nombres = {str(self.tabla_req.item(i, "values")[0]).lower() for i in self.tabla_req.get_children()}
        if nombre.lower() in nombres:
            messagebox.showerror("Nombre repetido", f"Ya existe una subred llamada '{nombre}'.", parent=self)
            return
        self.tabla_req.insert("", "end", values=(nombre, hosts))
        self.ent_nombre.delete(0, "end")
        self.ent_hosts.delete(0, "end")
        self.ent_nombre.focus_set()

    def quitar(self) -> None:
        for item in self.tabla_req.selection():
            self.tabla_req.delete(item)

    def vaciar_lista(self) -> None:
        vaciar(self.tabla_req)
        vaciar(self.tabla_out)
        self.lbl_resumen.configure(text="")
        self.ultimo_resultado = None

    def cargar_ejemplo(self) -> None:
        self.vaciar_lista()
        self.ent_base.delete(0, "end")
        self.ent_base.insert(0, self.EJEMPLO_BASE)
        for nombre, hosts in self.EJEMPLO_SUBREDES:
            self.tabla_req.insert("", "end", values=(nombre, hosts))
        self.calcular()

    # --- Cálculo -------------------------------------------------------------
    def calcular(self) -> None:
        requerimientos = [Requerimiento(*self.tabla_req.item(i, "values"))
                          for i in self.tabla_req.get_children()]
        try:
            resultado = calcular_vlsm(self.ent_base.get(), requerimientos)
        except ErrorEntrada as error:
            messagebox.showerror("No se pudo calcular", str(error), parent=self)
            return
        self.ultimo_resultado = resultado
        self.mostrar(resultado)

    def mostrar(self, r) -> None:
        vaciar(self.tabla_out)
        for i, s in enumerate(r.subredes):
            self.tabla_out.insert("", "end", tags=("par" if i % 2 == 0 else "impar",), values=(
                s.nombre, s.hosts_solicitados, s.hosts_validos, s.desperdicio, s.red_cidr,
                s.mascara, s.primer_host, s.ultimo_host, s.broadcast))
        texto = (f"Red base {r.red_base}/{r.prefijo_base}:  usadas {r.direcciones_usadas:,} de "
                 f"{r.direcciones_totales:,} direcciones ({r.porcentaje_usado:.2f} %)   |   "
                 f"libres {r.direcciones_libres:,}"
                 + (f" a partir de {r.siguiente_libre}" if r.siguiente_libre else "")
                 + f"   |   desperdicio total {r.desperdicio_total:,} hosts")
        if r.avisos:
            texto += "\nAviso: " + " ".join(r.avisos)
        self.lbl_resumen.configure(text=texto)

    def copiar(self) -> None:
        if self.ultimo_resultado is None:
            messagebox.showinfo("Sin resultados", "Primero realiza un cálculo.", parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(formatear_vlsm(self.ultimo_resultado))
        messagebox.showinfo("Copiado", "La tabla se copió al portapapeles.", parent=self)


# ===========================================================================
# Ventana principal
# ===========================================================================
class App(tk.Tk):
    TITULOS = {
        "ambas": "Calculadora IP — CIDR y VLSM",
        "cidr": "Calculadora IP (CIDR)",
        "vlsm": "Calculadora IP VLSM",
    }

    def __init__(self, modo: str = "ambas"):
        super().__init__()
        self.title(self.TITULOS.get(modo, self.TITULOS["ambas"]))
        self.geometry("1180x720")
        self.minsize(1000, 620)
        configurar_estilos(self)

        encabezado = tk.Frame(self, background=COLOR_PRINCIPAL)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text=self.TITULOS.get(modo, self.TITULOS["ambas"]), font=("Segoe UI", 15, "bold"),
                 fg="white", bg=COLOR_PRINCIPAL, pady=8, padx=14).pack(side="left")
        tk.Label(encabezado, text="Redes de Computadoras · ESCOM-IPN", font=("Segoe UI", 10),
                 fg="#F0DCE6", bg=COLOR_PRINCIPAL, padx=14).pack(side="right")

        if modo == "cidr":
            PanelCIDR(self).pack(fill="both", expand=True)
        elif modo == "vlsm":
            PanelVLSM(self).pack(fill="both", expand=True)
        else:
            pestanas = ttk.Notebook(self)
            pestanas.pack(fill="both", expand=True, padx=8, pady=8)
            pestanas.add(PanelCIDR(pestanas), text="Calculadora IP (CIDR)")
            pestanas.add(PanelVLSM(pestanas), text="Calculadora VLSM")


def iniciar(modo: str = "ambas") -> None:
    App(modo).mainloop()
