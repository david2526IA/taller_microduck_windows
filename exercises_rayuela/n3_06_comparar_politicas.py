"""NIVEL 3 - COMPARA TUS POLITICAS: ¿que cambia segun la recompensa con la que las entrenaste?

En n3_05 entrenas una politica de patada y se guarda en mis_politicas/<NOMBRE_POLITICA>.json. La idea del RL es esta:
LA MISMA tarea con DISTINTA recompensa da politicas con DISTINTA conducta. Aqui las pones a competir:
cada politica patea a cada casilla (1-9) y se mide si acierta y por cuantos metros falla. La tabla OFICIAL (la que mide Bravo
Robots con barridos de calibracion, no aprendida) entra como referencia.

COMO USARLO (unos 6 minutos en total):
  1. En n3_05 deja los valores por defecto y pon NOMBRE_POLITICA = "precisa". Ejecuta.
  2. Cambia PESO_FUERZA = 0.5 y NOMBRE_POLITICA = "ahorradora". Ejecuta.
  3. (opcional) CASILLAS = [3, 7] y NOMBRE_POLITICA = "solo_3_y_7": ¿generaliza a las casillas que no vio?
  4. Ejecuta este fichero: te da la tabla comparativa.
Predice antes de mirar: ¿que politica acierta mas? ¿cual se queda corta? ¿por que?
"""
import json, pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Que politicas comparas: nombres de fichero de mis_politicas/ sin .json. None = todas las que haya.
#   AFECTA A: la tabla. Con None entran todas las que hayas entrenado.
POLITICAS = None

# ¿Incluir la tabla OFICIAL (calibrada por Bravo Robots) como referencia?
#   AFECTA A: te da con que comparar. Si tu politica la iguala, has aprendido lo mismo que una calibracion a mano.
INCLUIR_OFICIAL = True

# Patadas por casilla (la fisica es casi determinista; con 1 basta, con 3 ves la variacion).
REPETICIONES = 1

# ====================================================================

import contextlib, io  # noqa: E402
import patada_env  # noqa: E402
from rayuela import board_geometry  # noqa: E402
import numpy as np  # noqa: E402


def evaluar(env, tabla):
    """Patea a cada casilla segun 'tabla' (dict casilla -> (pie, velocidad)) y devuelve aciertos y error medio (m)."""
    aciertos, errores, filas = 0, [], []
    for c in range(1, 10):
        pie, vel = tabla[c]
        for _ in range(REPETICIONES):
            x, y, cae, cayo = env.step(vel, pie)
            cx, cy = board_geometry.casilla_center(c)
            err = float(np.hypot(x - cx, y - cy))
            aciertos += cae == c
            errores.append(err)
            filas.append((c, cae, err))
    return aciertos, float(np.mean(errores)), filas


def main():
    carpeta = AQUI / "mis_politicas"
    nombres = POLITICAS or sorted(p.stem for p in carpeta.glob("*.json")) if carpeta.exists() else []
    tablas = {}
    for n in nombres:
        datos = json.loads((carpeta / f"{n}.json").read_text(encoding="utf-8"))
        tablas[n] = {int(c): (e["pie"], e["velocidad"]) for c, e in datos.items() if c.isdigit()}
    if INCLUIR_OFICIAL:
        tablas["oficial (calibrada)"] = {c: board_geometry.kick_for_casilla(c) for c in range(1, 10)}
    if not tablas:
        sys.exit("No hay politicas en mis_politicas/. Ejecuta antes n3_05_entrena_la_patada.py")
    print("Cargando el simulador...")
    with contextlib.redirect_stdout(io.StringIO()):
        env = patada_env.PatadaEnv()
    resultados = {}
    for n, t in tablas.items():
        with contextlib.redirect_stdout(io.StringIO()):
            resultados[n] = evaluar(env, {c: (p, v) for c, (p, v) in t.items()})
    print(f"\n{'politica':28s} | aciertos | error medio | por casilla (cae en ... , error m)")
    print("-" * 110)
    for n, (ac, em, filas) in resultados.items():
        det = "  ".join(f"{c}:{'OK' if cae == c else str(cae)}/{e:.2f}" for c, cae, e in filas[::REPETICIONES])
        print(f"{n:28s} |  {ac:2d}/{9 * REPETICIONES}   |  {em:6.2f} m   | {det}")
    mejor = max(resultados, key=lambda k: (resultados[k][0], -resultados[k][1]))
    print(f"\nLa que mas acierta: {mejor}.")
    for n in nombres:
        meta = json.loads((carpeta / f"{n}.json").read_text(encoding="utf-8")).get("_meta")
        if meta:
            print(f"  {n}: entrenada {meta['iteraciones']} rondas x {meta['patadas_por_ronda']} patadas, recompensa {meta['recompensa']}, casillas {meta['casillas_entrenadas']}")
    print("\nAhora: ¿por que se diferencian? Mira la recompensa de cada una. Es el diseño de la recompensa en accion.")


if __name__ == "__main__":
    main()
