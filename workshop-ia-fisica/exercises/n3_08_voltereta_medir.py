"""NIVEL 3 - LA VOLTERETA, CON NUMEROS: mide cada checkpoint y mira la curva de aprendizaje.

En n3_07 has VISTO la voltereta en distintos checkpoints. Aqui la MIDES: el programa hace que cada checkpoint intente la voltereta varias
veces (sin ventana, rapido) y cuenta cuantas veces sale bien. Es lo que se hace de verdad para elegir el mejor checkpoint de un entrenamiento.

QUE CUENTA COMO "SALE BIEN":  el tronco da (casi) una vuelta completa hacia delante (mas de 300 grados)  Y  el robot acaba de pie.

QUE VAS A VER:
  1. Una tabla: checkpoint -> cuantos intentos salieron bien.
  2. La CURVA del entrenamiento real (recompensa media segun las rondas). Si sube, el robot esta aprendiendo.
Tarda ~1 minuto con los valores por defecto.

PARA PENSAR: ¿coincide la curva con la tabla? La recompensa media sube y baja, y el exito tambien: el entrenamiento NO es una linea recta.
"""
import contextlib, csv, io, pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI.parent / "windows"))       # aqui vive el simulador sin ventana (voltereta_env)

# ============================ PARAMETROS ============================

# Checkpoints que mides (numeros de ronda). Disponibles: 0, 500, 750, 1250, 3000, 7000, 11000, 20000, 20750.
#   AFECTA A: las filas de la tabla. Mide solo dos (por ejemplo [750, 7000]) para que sea mas rapido.
CHECKPOINTS = [0, 750, 1250, 3000, 7000, 11000, 20000, 20750]

# Intentos por checkpoint (cada uno empieza con el robot de pie, tras esperar un tiempo ligeramente distinto).
#   AFECTA A: lo fiable que es la medida. Con 3 es rapido pero ruidoso; con 10 (el valor por defecto, ~2 minutos) es mas fiable.
#   La medida es REPRODUCIBLE: el mismo checkpoint con los mismos intentos da siempre la misma tabla.
INTENTOS = 10

# ¿Dibujar la curva del entrenamiento real?
MOSTRAR_CURVA = True

# ====================================================================


def curva(ruta):
    filas = [(int(r["iteracion"]), float(r["recompensa"])) for r in csv.DictReader(open(ruta, encoding="utf-8"))]
    print("\nCURVA DEL ENTRENAMIENTO REAL (recompensa media por ronda; cada # son ~2 puntos)\n  ronda | recompensa")
    for it, rew in filas:
        if it % 1250 == 0 or it == filas[-1][0]:
            print(f"  {it:5d} | {rew:6.1f} {'#' * max(0, int(rew / 2))}")


def main():
    import voltereta_env
    print("Cargando el simulador (unos segundos)...")
    with contextlib.redirect_stdout(io.StringIO()):
        env = voltereta_env.VolteretaEnv()
    carpeta = AQUI / "policies" / "voltereta"
    print(f"\n{'checkpoint':>10s} | salen bien | giro medio | que ha pasado\n" + "-" * 70)
    for ck in CHECKPOINTS:
        f = carpeta / f"voltereta_{ck:05d}.onnx"
        if not f.exists():
            print(f"{ck:>10d} | (no existe ese checkpoint)")
            continue
        bien, giros = 0, []
        for i in range(INTENTOS):
            with contextlib.redirect_stdout(io.StringIO()):
                giro, de_pie, _ = env.probar(f, segundos_asentar=0.8 + 0.1 * i)
            giros.append(giro)
            bien += giro > 300 and de_pie
        medio = sum(giros) / len(giros)
        if bien == INTENTOS:
            nota = "siempre"
        elif bien == 0:
            nota = "no gira" if medio < 60 else "gira a medias"
        else:
            nota = "a veces"
        print(f"{ck:>10d} | {bien:>4d} de {INTENTOS:<3d} | {medio:7.0f} gr  | {nota}", flush=True)
    if MOSTRAR_CURVA:
        curva(carpeta / "curva_entrenamiento.csv")
    print("\nSigue: ¿cual elegirias para llevar al robot real? ¿El ultimo? Mira el 20000.")


if __name__ == "__main__":
    main()
