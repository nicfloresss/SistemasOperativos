import tkinter as tk
from tkinter import ttk, messagebox
import operator
import random
from collections import deque

OPERACIONES = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": lambda a, b: round(a / b, 2),
    "%": operator.mod,
}
TAMANO_LOTE = 3
FUENTE = "Segoe UI"


def texto_operacion(p):
    return f"{p['operando1']} {p['operacion']} {p['operando2']}"


def generar_procesos(cantidad):
    procesos = []
    for i in range(1, cantidad + 1):
        tme = random.randint(7, 18)
        procesos.append({
            "id": i,
            "operacion": random.choice(list(OPERACIONES)),
            "operando1": random.randint(1, 100),
            "operando2": random.randint(1, 100),
            "tme": tme,
            "restante": tme,
            "ejecutado": 0,
            "resultado": None,
            "estado": "En espera",
        })
    return procesos


class SimuladorLotes:

    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("Simulador de Procesamiento por Lotes")
        ventana.geometry("1050x700")
        ventana.minsize(900, 620)

        self._reiniciar_estado()
        self._estilos()
        self._crear_interfaz()
        ventana.bind("<Key>", self.manejar_tecla)

    # ------------------------------------------------------------------
    # Estado
    # ------------------------------------------------------------------
    def _reiniciar_estado(self):
        self.lotes, self.lote, self.terminados = [], [], []
        self.cola = deque()
        self.actual = None
        self.indice = 0
        self.reloj = 0
        self.en_ejecucion = self.pausado = self.finalizado = False
        self.after_id = None

    def _activo(self):
        return self.en_ejecucion and not self.pausado and not self.finalizado

    # ------------------------------------------------------------------
    # Interfaz
    # ------------------------------------------------------------------
    def _estilos(self):
        e = ttk.Style()
        e.theme_use("clam")
        azul = "#1f3a5f"
        e.configure("TLabel", font=(FUENTE, 10))
        e.configure("Titulo.TLabel", font=(FUENTE, 16, "bold"), foreground=azul)
        e.configure("Dato.TLabel", font=(FUENTE, 11, "bold"), foreground=azul)
        e.configure("Estado.TLabel", font=(FUENTE, 10, "italic"),
                    background="#e8f0fe", padding=6)
        e.configure("TLabelframe.Label", font=(FUENTE, 10, "bold"), foreground=azul)
        e.configure("TButton", font=(FUENTE, 10), padding=5)
        e.configure("Treeview", rowheight=26, font=(FUENTE, 10))
        e.configure("Treeview.Heading", font=(FUENTE, 10, "bold"))

    @staticmethod
    def _marco(padre, titulo, **opciones):
        marco = ttk.LabelFrame(padre, text=titulo, padding=10)
        marco.pack(**opciones)
        return marco

    @staticmethod
    def _tabla(padre, columnas):
        tabla = ttk.Treeview(padre, columns=[c[0] for c in columnas],
                             show="headings", height=8)
        for clave, titulo, ancho in columnas:
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho, anchor="center")
        tabla.tag_configure("Ejecutando", background="#d4edda")
        tabla.tag_configure("Terminado", background="#eef6ff")
        tabla.tag_configure("Error", background="#f8d7da")
        tabla.pack(fill="both", expand=True)
        return tabla

    def _crear_interfaz(self):
        principal = ttk.Frame(self.ventana, padding=12)
        principal.pack(fill="both", expand=True)

        ttk.Label(principal, text="Simulador de Procesamiento por Lotes",
                  style="Titulo.TLabel").pack(anchor="w", pady=(0, 8))

        # Configuración
        config = self._marco(principal, "Configuración inicial", fill="x")
        ttk.Label(config, text="Número de trabajos:").pack(side="left", padx=5)
        self.entrada_n = ttk.Entry(config, width=10)
        self.entrada_n.pack(side="left", padx=5)
        self.entrada_n.bind("<Return>", lambda _: self.iniciar_simulacion())
        self.entrada_n.focus()
        self.boton_iniciar = ttk.Button(config, text="Iniciar simulación",
                                        command=self.iniciar_simulacion)
        self.boton_iniciar.pack(side="left", padx=5)
        ttk.Button(config, text="Nueva simulación",
                   command=self.reiniciar).pack(side="left", padx=5)

        # Información general
        info = ttk.Frame(principal)
        info.pack(fill="x", pady=8)
        self.var_lote = tk.StringVar()
        self.var_pendientes = tk.StringVar()
        self.var_reloj = tk.StringVar()
        for var in (self.var_lote, self.var_pendientes, self.var_reloj):
            ttk.Label(info, textvariable=var, style="Dato.TLabel").pack(side="left", padx=15)

        self.var_estado = tk.StringVar(value="Esperando iniciar la simulación.")
        ttk.Label(principal, textvariable=self.var_estado,
                  style="Estado.TLabel").pack(fill="x", pady=(0, 8))

        # Zona central
        centro = ttk.Frame(principal)
        centro.pack(fill="both", expand=True)

        lote_frame = self._marco(centro, "Procesos del lote actual",
                                 side="left", fill="both", expand=True, padx=5)
        self.tabla_lote = self._tabla(lote_frame, [
            ("id", "ID", 60), ("tme", "TME", 80),
            ("restante", "Tiempo restante", 120), ("estado", "Estado", 110)])

        ejec_frame = self._marco(centro, "Proceso en ejecución",
                                 side="left", fill="both", expand=True, padx=5)
        self.datos = {}
        for fila, campo in enumerate(("ID", "Operación", "TME",
                                      "Tiempo ejecutado", "Tiempo restante")):
            self.datos[campo] = tk.StringVar()
            ttk.Label(ejec_frame, text=f"{campo}:").grid(row=fila, column=0, sticky="w", pady=8)
            ttk.Label(ejec_frame, textvariable=self.datos[campo],
                      style="Dato.TLabel").grid(row=fila, column=1, sticky="w", padx=10)

        # Controles (los botones y las teclas comparten la misma lista)
        controles = self._marco(principal, "Controles", fill="x", pady=10)
        self.teclas = {}
        for tecla, texto, comando in (
            ("i", "I - Interrupción E/S", self.interrumpir),
            ("e", "E - Error", self.error_proceso),
            ("p", "P - Pausa", self.pausar),
            ("c", "C - Continuar", self.continuar),
        ):
            ttk.Button(controles, text=texto, command=comando).pack(side="left", padx=5)
            self.teclas[tecla] = comando

        # Terminados
        fin_frame = self._marco(principal, "Trabajos terminados", fill="both", expand=True)
        self.tabla_terminados = self._tabla(fin_frame, [
            ("id", "ID", 70), ("operacion", "Operación", 250), ("resultado", "Resultado", 150)])

        self.actualizar()

    # ------------------------------------------------------------------
    # Simulación
    # ------------------------------------------------------------------
    def iniciar_simulacion(self):
        if self.en_ejecucion:
            return
        try:
            cantidad = int(self.entrada_n.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número de trabajos mayor a 0.")
            return

        procesos = generar_procesos(cantidad)
        self.lotes = [procesos[i:i + TAMANO_LOTE]
                      for i in range(0, len(procesos), TAMANO_LOTE)]
        self.indice, self.reloj, self.terminados = 0, 0, []
        self.en_ejecucion, self.pausado, self.finalizado = True, False, False

        self.entrada_n.config(state="disabled")
        self.boton_iniciar.config(state="disabled")

        self._cargar_lote()
        self.var_estado.set("Simulación en ejecución.")
        self.actualizar()
        self.programar()

    def _cargar_lote(self):
        self.lote = self.lotes[self.indice]
        self.cola = deque(self.lote)
        self._siguiente()

    def _siguiente(self):
        """Toma el siguiente proceso del lote; si no quedan, pasa al siguiente lote."""
        if self.cola:
            self.actual = self.cola.popleft()
            self.actual["estado"] = "Ejecutando"
            return

        self.actual = None
        self.indice += 1
        if self.indice < len(self.lotes):
            self._cargar_lote()
            self.var_estado.set(f"Inició el lote {self.indice + 1}")
        else:
            self.finalizar()

    def finalizar(self):
        self.cancelar()
        self.en_ejecucion, self.pausado, self.finalizado = False, False, True
        self.actual = None
        self.var_estado.set("Todos los procesos han terminado. Simulación finalizada.")

    # ------------------------------------------------------------------
    # Reloj
    # ------------------------------------------------------------------
    def programar(self):
        if self._activo():
            self.after_id = self.ventana.after(1000, self.tick)

    def cancelar(self):
        if self.after_id is not None:
            try:
                self.ventana.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

    def tick(self):
        self.after_id = None
        if not self._activo() or self.actual is None:
            return

        p = self.actual
        p["ejecutado"] += 1
        p["restante"] -= 1
        self.reloj += 1

        if p["restante"] <= 0:
            p["restante"] = 0
            p["resultado"] = OPERACIONES[p["operacion"]](p["operando1"], p["operando2"])
            p["estado"] = "Terminado"
            self.terminados.append(p)
            self._siguiente()

        self.actualizar()
        self.programar()

    # ------------------------------------------------------------------
    # Controles
    # ------------------------------------------------------------------
    def manejar_tecla(self, evento):
        accion = self.teclas.get(evento.keysym.lower())
        if accion and self.en_ejecucion:
            accion()

    def _puede_actuar(self):
        return self._activo() and self.actual is not None

    def interrumpir(self):
        if not self._puede_actuar():
            return
        self.cancelar()
        p = self.actual
        p["estado"] = "En espera"
        self.cola.append(p)            # va al final de la cola del lote
        self._siguiente()
        self.var_estado.set(f"Proceso {p['id']} interrumpido por E/S. "
                            "Se envió al final de la cola.")
        self.actualizar()
        self.programar()

    def error_proceso(self):
        if not self._puede_actuar():
            return
        self.cancelar()
        p = self.actual
        p.update(resultado="ERROR", estado="Error", restante=0)
        self.terminados.append(p)
        self._siguiente()
        if not self.finalizado:
            self.var_estado.set(f"Proceso {p['id']} terminado por ERROR.")
        self.actualizar()
        self.programar()

    def pausar(self):
        if not self._activo():
            return
        self.pausado = True
        self.cancelar()
        self.var_estado.set("SIMULACIÓN PAUSADA. Presiona C para continuar.")

    def continuar(self):
        if not (self.en_ejecucion and self.pausado):
            return
        self.pausado = False
        self.var_estado.set("Simulación reanudada.")
        self.programar()

    # ------------------------------------------------------------------
    # Pantalla
    # ------------------------------------------------------------------
    @staticmethod
    def _llenar(tabla, filas):
        tabla.delete(*tabla.get_children())
        for valores, etiqueta in filas:
            tabla.insert("", "end", values=valores, tags=(etiqueta,))

    def actualizar(self):
        total = len(self.lotes)
        self.var_lote.set(f"Lote actual: {min(self.indice + 1, total)} de {total}"
                          if total else "Lote actual: -")
        self.var_pendientes.set(f"Lotes pendientes: {max(total - self.indice - 1, 0)}")
        self.var_reloj.set(f"Reloj global: {self.reloj} segundos")

        self._llenar(self.tabla_lote, [
            ((p["id"], p["tme"], p["restante"], p["estado"]), p["estado"])
            for p in self.lote])

        p = self.actual
        valores = (p["id"], texto_operacion(p), f"{p['tme']} segundos",
                   f"{p['ejecutado']} segundos", f"{p['restante']} segundos") if p else ("-",) * 5
        for variable, valor in zip(self.datos.values(), valores):
            variable.set(valor)

        self._llenar(self.tabla_terminados, [
            ((t["id"], texto_operacion(t), t["resultado"]), t["estado"])
            for t in self.terminados])

    def reiniciar(self):
        self.cancelar()
        self._reiniciar_estado()
        self.entrada_n.config(state="normal")
        self.entrada_n.delete(0, tk.END)
        self.entrada_n.focus()
        self.boton_iniciar.config(state="normal")
        self.var_estado.set("Esperando iniciar la simulación.")
        self.actualizar()

if __name__ == "__main__":
    ventana = tk.Tk()
    SimuladorLotes(ventana)
    ventana.mainloop()