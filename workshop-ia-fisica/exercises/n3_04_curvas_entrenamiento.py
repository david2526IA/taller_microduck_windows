"""NIVEL 3 - Entrenar un cerebro: ¿que pasa si cambio un parametro?
Estas curvas son REALES: las sacamos entrenando el mismo robot (levantarse del suelo) 100 rondas,
cambiando UN solo parametro cada vez. Tu no necesitas GPU: aqui las comparas.

COMO SE USA
  1) ANTES de marcar una casilla, lee que se cambio en ese experimento.
  2) Marca la casilla: aparece la curva. ¿Acertaste?
  3) Cambia de grafica (recompensa / cuanto aguanta / exploracion) y el eje de abajo (rondas / minutos).
  Si la curva SUBE, el robot esta aprendiendo. Cuanto antes suba, mejor entrenado va.
  Si una curva "se sale de la grafica", es que se ha descontrolado por completo.

Los datos estan en entrenar/resultados/*.csv (uno por experimento).
"""
import csv, pathlib, tkinter as tk

# nombre del fichero -> (etiqueta, que se cambio, color)
EXPERIMENTOS = {
    "base":          ("Base", "Nada: el entrenamiento normal (4096 robots, aprendizaje 0,001)", "#1b6ca8"),
    "pocos_robots":  ("Pocos robots", "num-envs 256 en vez de 4096: 16 veces menos robots a la vez", "#d9822b"),
    "lr_alto":       ("Aprendizaje alto", "learning-rate 0,01: pasos 10 veces mas grandes al ajustar", "#c0392b"),
    "lr_bajo":       ("Aprendizaje bajo", "learning-rate 0,00005: pasos 20 veces mas pequeños", "#2e9e6b"),
    "exploracion":   ("Mucha exploracion", "entropy-coef 0,1: premia probar cosas raras (10 veces mas)", "#8e5bb5"),
    "miopia":        ("Miope", "gamma 0,8: solo le importa el futuro cercano. ¿Le hara falta mirar lejos aqui?", "#7f8c8d"),
    "largo":         ("Largo (300 rondas)", "El entrenamiento completo del taller: 300 rondas en vez de 100", "#222222"),
}
GRAFICAS = {
    "recompensa":        ("Recompensa media (sube = aprende)", "puntos"),
    "duracion_episodio": ("Cuanto aguanta antes de acabar el intento", "pasos (max 300)"),
    "exploracion":       ("Exploracion: cuanto varia lo que prueba (baja = decidido)", "desviacion"),
}
EJES = {"rondas": "Rondas de entrenamiento", "minutos": "Minutos de entrenamiento (GPU RTX 4090)"}

carpeta = pathlib.Path(__file__).resolve().parent.parent / "entrenar" / "resultados"
datos = {}
for nombre in EXPERIMENTOS:
    f = carpeta / f"{nombre}.csv"
    if f.exists():
        with open(f, newline="") as fh:
            datos[nombre] = list(csv.DictReader(fh))
if not datos:
    raise SystemExit(f"No encuentro los datos en {carpeta}")

raiz = tk.Tk()
raiz.title("Curvas de entrenamiento · Microduck")
raiz.geometry("1100x780")
inicial = "base" if "base" in datos else next(iter(datos))
marcadas = {n: tk.BooleanVar(value=(n == inicial)) for n in datos}
grafica = tk.StringVar(value="recompensa")
eje = tk.StringVar(value="rondas")

izq = tk.Frame(raiz, padx=12, pady=10); izq.pack(side="left", fill="y")
tk.Label(izq, text="1 · Predice  2 · Marca", font=("Segoe UI", 13, "bold")).pack(anchor="w")
for n, v in marcadas.items():
    etiqueta, cambio, color = EXPERIMENTOS[n]
    fila = tk.Frame(izq); fila.pack(anchor="w", pady=3, fill="x")
    tk.Checkbutton(fila, variable=v, command=lambda: dibujar(), fg=color, activeforeground=color,
                   text=etiqueta, font=("Segoe UI", 11, "bold")).pack(anchor="w")
    tk.Label(fila, text=cambio, wraplength=300, justify="left", fg="#555", font=("Segoe UI", 9)).pack(anchor="w", padx=22)
tk.Label(izq, text="Gráfica", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(12, 2))
for clave, (titulo, _) in GRAFICAS.items():
    tk.Radiobutton(izq, text=titulo, value=clave, variable=grafica, command=lambda: dibujar(),
                   wraplength=300, justify="left").pack(anchor="w")
tk.Label(izq, text="Eje horizontal", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(12, 2))
for clave in EJES:
    tk.Radiobutton(izq, text=clave.capitalize(), value=clave, variable=eje, command=lambda: dibujar()).pack(anchor="w")
der = tk.Frame(raiz); der.pack(side="right", fill="both", expand=True, padx=8, pady=8)
resumen = tk.Label(der, text="", justify="left", anchor="w", wraplength=700, font=("Segoe UI", 10), fg="#222")
resumen.pack(side="bottom", fill="x", pady=(6, 0))
lienzo = tk.Canvas(der, bg="white", highlightthickness=0)
lienzo.pack(side="top", fill="both", expand=True)
lienzo.bind("<Configure>", lambda e: dibujar())


def serie(nombre, clave):
    """Lista de (x, y); x en rondas o en minutos segun el eje elegido."""
    if eje.get() == "minutos":
        return [(float(f["segundos"]) / 60, float(f[clave])) for f in datos[nombre]]
    return [(int(f["iteracion"]), float(f[clave])) for f in datos[nombre]]


def dibujar():
    lienzo.delete("all")
    ancho, alto = lienzo.winfo_width(), lienzo.winfo_height()
    if ancho < 50:
        return
    izq_m, der_m, arr_m, aba_m = 70, 20, 50, 50
    clave = grafica.get()
    elegidas = [n for n in datos if marcadas[n].get()]
    titulo, unidad = GRAFICAS[clave]
    lienzo.create_text(izq_m, 22, anchor="w", text=titulo, font=("Segoe UI", 13, "bold"))
    if not elegidas:
        lienzo.create_text(ancho / 2, alto / 2, text="Marca una casilla para ver su curva", fill="#888", font=("Segoe UI", 14))
        resumen.config(text="")
        return
    # Limites de la grafica: los de la curva "base" ampliados 5 veces. Lo que se sale, se recorta (se ha descontrolado).
    ref = [y for _, y in serie(inicial if "base" not in datos else "base", clave)]
    amplitud = (max(ref) - min(ref)) or 1
    tope_bajo, tope_alto = min(ref) - 5 * amplitud, max(ref) + 5 * amplitud
    recortadas = []
    puntos_por_curva = {}
    for n in elegidas:
        pts = []
        for x, y in serie(n, clave):
            pts.append((x, min(max(y, tope_bajo), tope_alto)))
        puntos_por_curva[n] = pts
        if any(not (tope_bajo <= y <= tope_alto) for _, y in serie(n, clave)):
            recortadas.append(n)
    todas = [p for pts in puntos_por_curva.values() for p in pts]
    xmax = max(p[0] for p in todas) or 1
    ymin = min(0, min(p[1] for p in todas)); ymax = max(p[1] for p in todas)
    ymax = ymax + (ymax - ymin) * 0.05 or 1
    px = lambda x: izq_m + (ancho - izq_m - der_m) * x / xmax
    py = lambda y: alto - aba_m - (alto - aba_m - arr_m) * (y - ymin) / (ymax - ymin)
    for i in range(6):
        y = ymin + (ymax - ymin) * i / 5
        lienzo.create_line(izq_m, py(y), ancho - der_m, py(y), fill="#eee")
        lienzo.create_text(izq_m - 8, py(y), anchor="e", text=f"{y:.2f}" if ymax < 5 else f"{y:.0f}", fill="#666")
    for i in range(6):
        x = xmax * i / 5
        lienzo.create_text(px(x), alto - aba_m + 14, text=f"{x:.0f}" if eje.get() == "rondas" else f"{x:.1f}", fill="#666")
    lienzo.create_text(ancho / 2, alto - 12, text=EJES[eje.get()], fill="#666")
    lienzo.create_text(14, alto / 2, text=unidad, angle=90, fill="#666")
    for n in elegidas:
        pts = [(px(x), py(y)) for x, y in puntos_por_curva[n]]
        lienzo.create_line(*[c for p in pts for c in p], fill=EXPERIMENTOS[n][2], width=3, smooth=True)
    for i, n in enumerate(recortadas):
        lienzo.create_text(ancho - der_m - 6, alto - aba_m - 14 - 18 * i, anchor="e", fill=EXPERIMENTOS[n][2],
                           font=("Segoe UI", 11, "bold"), text=f"{EXPERIMENTOS[n][0]}: se descontrola y se sale de la gráfica")
    # Resumen: recompensa final y en que momento llega a la mitad de lo que consigue la base
    base = float(datos["base"][-1]["recompensa"]) if "base" in datos else None
    texto = []
    for n in elegidas:
        filas = datos[n]
        final = float(filas[-1]["recompensa"])
        s = f"{EXPERIMENTOS[n][0]}: recompensa final {final:.1f}" if abs(final) < 1000 else f"{EXPERIMENTOS[n][0]}: se ha descontrolado"
        if base and abs(final) < 1000:
            fila = next((f for f in filas if float(f["recompensa"]) >= 0.5 * base), None)
            s += (f" · mitad de la base en la ronda {fila['iteracion']}" if fila else " · NO llega a la mitad de la base")
        s += f" · {float(filas[-1]['segundos']) / 60:.1f} min"
        texto.append(s)
    resumen.config(text="\n".join(texto))


dibujar()
raiz.mainloop()
