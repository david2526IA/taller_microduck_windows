"""CASO DE USO 5 (b) - VALIDAR POLITICAS EN EL CIRCUITO: ¿cual aguanta mas, y donde se rompe?

Es la parte de VALIDACION de la demo de NVIDIA del GTC Berlin: antes de fiarte de una politica, la pruebas muchas veces en
simulacion y mides circuitos completados, caidas y en que seccion se caen. Aqui lo hace tu PC en CPU, sin ventana:
lanza PRUEBAS recorridos por cada combinacion de cerebro y nivel (con un pequeño azar al salir) y escribe una tabla.

Los cerebros: alpha_walking (entrenado en llano) frente a rough_walk_e y rough_walk_g (entrenados en terreno irregular, de Hugging Face).
Los niveles: el CRESCENDO del circuito (0 llano ... 4 rampa + escalones + cuadricula + escombros).
Tarda unos minutos con los valores por defecto. El resultado se guarda tambien en validacion_obstaculos.csv.

EXPERIMENTOS: cambia UN valor, guarda (Ctrl+S) y ejecuta (F5).
"""
import csv, pathlib, sys, time

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Cuantos recorridos por cada combinacion. Mas = numeros mas fiables (y mas tiempo). Con 4 sale ruidoso; con 20 es mas serio.
PRUEBAS = 6

# Que cerebros comparas (nombres, o rutas a tus .onnx).
CEREBROS = ["alpha_walking", "rough_walk_e", "rough_walk_g"]

# Que niveles pruebas (0 llano ... 4 rampa + escalones + cuadricula + escombros).
NIVELES = [0, 1, 2, 3, 4]

# Velocidad pedida (m/s). La bateria de Pollen usa 0.3; con 0.4 (el maximo entrenado) se llega a la meta en ~35 s.
AVANCE = 0.4

# ¿Corrige el rumbo para ir recto? Sin ello cada cerebro se desvia a su manera y no se mide el obstaculo sino el desvio.
MANTENER_RUMBO = True

# El circuito (mismas piezas que en n4_05): sube la altura de los escalones a 0.02 y mira como cambia todo.
ALTURA_ESCALON = 0.010
ALTURA_CUADRICULA = 0.010
ALTURA_ESCOMBROS = 0.015
ANGULO_RAMPA = 6.0

# ====================================================================

import obstaculos  # noqa: E402

if __name__ == "__main__":
    print(__doc__)
    t0 = time.time()
    cabecera = f"{'nivel':32s}" + "".join(f"{str(c)[-18:]:>22s}" for c in CEREBROS)
    print(cabecera + "\n" + "-" * len(cabecera), flush=True)
    filas = []
    for nv in NIVELES:
        fila = f"{obstaculos.NIVELES[nv]:32s}"
        for c in CEREBROS:
            r = obstaculos.evaluar(c, pruebas=PRUEBAS, avance=AVANCE, semilla=1, mantener_rumbo=MANTENER_RUMBO,
                                   cfg=dict(nivel=nv, altura_escalon=ALTURA_ESCALON, altura_cuadricula=ALTURA_CUADRICULA,
                                            altura_escombros=ALTURA_ESCOMBROS, angulo_rampa=ANGULO_RAMPA))
            fila += f"{str(r['completados']) + '/' + str(PRUEBAS) + ' (llega a x=' + format(r['distancia_media'], '.1f') + ')':>22s}"
            filas.append(dict(nivel=nv, cerebro=str(c), completados=r["completados"], pruebas=PRUEBAS, caidas=r["caidas"],
                              atascados=r["atascados"], distancia_media=round(r["distancia_media"], 2), caidas_en=str(r["caidas_en"])))
        print(fila, flush=True)
    print(f"\n(completados / pruebas, y hasta donde llegan de media; la meta esta a x={obstaculos.X_FIN} m)  [{time.time() - t0:.0f} s]")
    with open(AQUI / "validacion_obstaculos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print("Guardado: validacion_obstaculos.csv")
