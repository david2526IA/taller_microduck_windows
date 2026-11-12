"""Convierte las curvas de TensorBoard de los experimentos en CSV pequenos (los que lee el ejercicio n3_04).
Uso (con el python del proyecto de entrenamiento):
  .venv/bin/python exportar_curvas.py  <carpeta_logs/rsl_rl>  <carpeta_salida>  [nombre=carpeta ...]
Cada CSV: iteracion, recompensa, duracion_episodio, exploracion, segundos
"""
import csv, glob, os, sys
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

COLUMNAS = {"recompensa": "Train/mean_reward", "duracion_episodio": "Train/mean_episode_length",
            "exploracion": "Policy/mean_std"}

def exportar(carpeta_run, destino):
    ficheros = sorted(glob.glob(os.path.join(carpeta_run, "events*")))
    ea = EventAccumulator(ficheros[0], size_guidance={"scalars": 0}); ea.Reload()
    series = {k: ea.Scalars(t) for k, t in COLUMNAS.items()}
    n = len(series["recompensa"]); t0 = series["recompensa"][0].wall_time
    with open(destino, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["iteracion", *COLUMNAS, "segundos"])
        for i in range(n):
            w.writerow([series["recompensa"][i].step, *[round(series[k][i].value, 4) for k in COLUMNAS],
                        round(series["recompensa"][i].wall_time - t0, 1)])
    return n

if __name__ == "__main__":
    logs, salida, *pares = sys.argv[1:]
    os.makedirs(salida, exist_ok=True)
    for par in pares:
        nombre, carpeta = par.split("=")
        run = sorted(glob.glob(os.path.join(logs, carpeta, "*")))[-1] if "*" not in carpeta else glob.glob(os.path.join(logs, carpeta))[0]
        print(nombre, exportar(run, os.path.join(salida, nombre + ".csv")), "filas")
