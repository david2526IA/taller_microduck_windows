"""BLOQUE 6 - GENERALIZAR: ¿tu politica aguanta un mundo distinto del que vio al entrenar?

La brecha entre simulacion y realidad es esta: el robot real nunca es EXACTAMENTE el robot simulado (otro suelo, otra masa,
otra pelota). Todo esto, simulado: aqui "el mundo real" son mundos de prueba con valores distintos a los de entrenamiento.

EJECUTALO YA (viene con tres politicas de ejemplo ya entrenadas; tarda ~1 minuto) y mira la tabla. Tres politicas, la misma tarea:
  un_solo_mundo    entrenada en UN mundo (60 rondas).   Acierta 8 de 9 ahi... y se hunde en cuanto el mundo cambia un poco.
  mundos_variados  entrenada en mundos al azar, A CIEGAS (60 rondas). No sabe en que mundo esta: solo aprende un promedio. Empeora.
  percibe150       entrenada en mundos al azar y VIENDO como es el mundo (150 rondas). Se adapta: aguanta mundos que no vio.
(Los numeros medidos con estas tres estan en PROGRAMA.md y en las diapositivas. La oficial es una tabla calibrada a mano.)

LA LECCION: aleatorizar el mundo no basta; la politica tiene que poder PERCIBIR lo que cambia (en el robot real: sensores,
o una estimacion a partir de lo que acaba de pasar). Y entrenar con variedad cuesta mas rondas.

DESPUES, ENTRENA LAS TUYAS en n3_05_entrena_la_patada.py (cambia UN grupo de parametros cada vez):
  - ALEATORIZAR = 0.25, VE_EL_MUNDO = False  -> a ciegas (unos 4 min).
  - ALEATORIZAR = 0.25, VE_EL_MUNDO = True, ITERACIONES = 150 -> percibe el mundo (unos 6 min).
  Pon un NOMBRE_POLITICA distinto en cada una y anadelos a POLITICAS aqui abajo.
"""
import contextlib, io, json, pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Que politicas comparas: nombres sin .json. Busca primero en mis_politicas/ (las que entrenas tu) y despues en
# windows/politicas/ejemplos/ (las tres de ejemplo).
#   AFECTA A: las columnas de la tabla. Entrena las tuyas en n3_05 y ponlas aqui.
POLITICAS = ["un_solo_mundo", "mundos_variados", "percibe150"]

# Los mundos de prueba: (nombre, factor de gravedad, factor de masa de la pelota, factor de rozamiento de la pelota).
#   1.0 = como en entrenamiento. AFECTA A: lo dificil que es la prueba. Inventa los tuyos: ¿hasta donde aguanta cada politica?
MUNDOS_PRUEBA = [
    ("Normal",                   1.0, 1.0, 1.0),
    ("Rozamiento un poco menor", 1.0, 1.0, 0.8),
    ("Rozamiento un poco mayor", 1.0, 1.0, 1.25),
    ("Pelota mas pesada",        1.0, 1.4, 1.0),
    ("Gravedad menor",           0.8, 1.0, 1.0),
    ("Todo a la vez",            1.15, 1.3, 1.2),
]

# ¿Incluir la tabla OFICIAL (calibrada a mano por Bravo Robots) como referencia?
INCLUIR_OFICIAL = True

# ====================================================================

import patada_env  # noqa: E402
from rayuela import board_geometry  # noqa: E402


def _entrenador():
    """Carga n3_05 como modulo: de ahi sale la clase Politica (la red) y observacion()."""
    import importlib.util
    s = importlib.util.spec_from_file_location("n3_05", AQUI / "exercises_rayuela" / "n3_05_entrena_la_patada.py")
    mod = importlib.util.module_from_spec(s)
    with contextlib.redirect_stdout(io.StringIO()):
        s.loader.exec_module(mod)
    return mod


def cargar(carpeta, nombre):
    """Devuelve una funcion (casilla, contexto_del_mundo) -> (pie, velocidad)."""
    datos = json.loads((carpeta / f"{nombre}.json").read_text(encoding="utf-8"))
    if "_red" in datos:                                  # politica que PERCIBE el mundo: hay que ejecutar su red
        import numpy as np
        mod = _entrenador()
        pol = mod.Politica(np.random.default_rng(0), 0.1, entradas=5)
        pol.p = {k: np.asarray(v) for k, v in datos["_red"].items()}
        a = datos["_meta"]["mundo"].get("aleatorizar") or 0.3
        def actuar(c, factores):
            ctx = tuple((f - 1) / a for f in factores)
            v, pie = pol.actuar(mod.observacion(c, ctx, ve_mundo=True), None, determinista=True)
            return mod.PIES[pie], float(min(max(v, mod.VEL_MIN), mod.VEL_MAX))
        return actuar
    tabla = {int(c): (e["pie"], e["velocidad"]) for c, e in datos.items() if c.isdigit()}
    return lambda c, factores: tabla[c]                  # una tabla fija: no percibe nada


def aciertos_en(env, politica, factores):
    ok = 0
    for c in range(1, 10):
        pie, vel = politica(c, factores)
        with contextlib.redirect_stdout(io.StringIO()):
            ok += env.step(vel, pie)[2] == c
    return ok


def main():
    tablas = {}
    for n in POLITICAS:
        for carpeta in (AQUI / "mis_politicas", AQUI / "windows" / "politicas" / "ejemplos"):
            if (carpeta / f"{n}.json").exists():
                tablas[n] = cargar(carpeta, n)
                break
        else:
            print(f"(falta {n}.json: entrenala en n3_05 con NOMBRE_POLITICA = \"{n}\")")
    if INCLUIR_OFICIAL:
        oficial = {c: board_geometry.kick_for_casilla(c) for c in range(1, 10)}
        tablas["oficial"] = lambda c, factores: oficial[c]
    if not tablas:
        sys.exit("No hay politicas que comparar. Entrena primero con n3_05_entrena_la_patada.py")
    print("Cargando el simulador...")
    with contextlib.redirect_stdout(io.StringIO()):
        env = patada_env.PatadaEnv()
    g0, m0, r0 = 9.81, env.base_masa, float(env.base_roz[0])
    cab = " | ".join(f"{n[:16]:>16s}" for n in tablas)
    print(f"\nACIERTOS de 9 casillas en cada mundo\n{'mundo de prueba':28s} | {cab}\n" + "-" * (31 + 19 * len(tablas)))
    suma = {n: 0 for n in tablas}
    for nombre, fg, fm, fr in MUNDOS_PRUEBA:
        env.set_mundo(g0 * fg, m0 * fm, r0 * fr)
        fila = {n: aciertos_en(env, t, (fg, fm, fr)) for n, t in tablas.items()}
        for n, v in fila.items():
            suma[n] += v
        print(f"{nombre:28s} | " + " | ".join(f"{fila[n]:>13d}/9 " for n in tablas), flush=True)
    print("-" * (31 + 19 * len(tablas)))
    print(f"{'MEDIA':28s} | " + " | ".join(f"{suma[n] / len(MUNDOS_PRUEBA):>13.1f}/9 " for n in tablas))
    print("\nLectura: la que acierta mucho en 'Normal' pero cae en cuanto el mundo cambia esta SOBREAJUSTADA a un solo mundo: esa es la brecha sim-to-real en pequeño.")
    print("Entrenar con el mundo al azar A CIEGAS no lo arregla (solo aprende un promedio). Lo arregla la que PERCIBE lo que cambia.")


if __name__ == "__main__":
    main()
