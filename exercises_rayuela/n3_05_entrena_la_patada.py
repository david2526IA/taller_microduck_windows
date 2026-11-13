"""NIVEL 3 - ENTRENA TU PROPIA POLITICA DE PATADA (RL con PPO, en tu PC, sin GPU).

El cerebro de patada del Microduck (el .onnx) ya sabe patear a la velocidad que se le pida. Lo que vas a entrenar
aqui es el nivel de ARRIBA: una politica pequeña que, viendo en que casilla hay que meter la pelota, DECIDE
con que pie y a que velocidad patear. Es el mismo bucle que el entrenamiento real de mjlab, en pequeño:

   1. la politica elige una accion (pie, velocidad)            <- AGENTE
   2. el simulador patea y deja la pelota en un sitio          <- ENTORNO  (windows/patada_env.py, MuJoCo + cerebro ONNX)
   3. una formula puntua lo que paso                           <- RECOMPENSA (la defines tu, abajo)
   4. PPO ajusta la politica para repetir lo que puntuo bien   <- ALGORITMO

   observacion = donde esta la casilla objetivo   |   accion = (pie, velocidad en m/s)   |   1 patada = 1 episodio
(Como cada episodio es una sola patada, gamma y GAE no pintan nada aqui; en el robot real si, por eso el
entrenamiento de verdad usa GPU y miles de robots a la vez.)

EL ENTORNO POR DENTRO (asi es TODO entorno de RL, el de la patada y el de cualquier robot)
Un entorno es un objeto con dos operaciones y una nota:
   reset()          deja el mundo en el punto de partida:  el pato de pie, la pelota delante del pie.
   step(accion)     ejecuta UNA accion y devuelve que paso:  "patea a 0,9 m/s con el pie derecho" -> "la pelota se paro en la casilla 7".
   recompensa       la nota de ese resultado: mas puntos cuanto mas cerca de la casilla pedida. Esta mas abajo: leela y cambiala.
Y cuatro decisiones de DISENO, que son lo dificil del RL:
   que VE el cerebro (observacion) · que PUEDE HACER (accion) · que se PREMIA (recompensa) · cuando ACABA el intento (terminacion: aqui, tras la patada,
   o si el pato se cae). Si algo no funciona, casi siempre hay que volver a una de estas cuatro, o al mundo (el modelo), o a los botones de PPO.

COMO USARLO: cambia UN parametro, guarda (Ctrl+S) y ejecuta (F5). Mira la curva y la tabla final.
   Cada patada simulada tarda ~1 s: 60 rondas x 12 patadas = unos 3 minutos.
Al terminar se guarda  mis_politicas/<NOMBRE_POLITICA>.json  y puedes jugar la rayuela con TU politica (n4_00, TABLA_PROPIA).
"""
import json, pathlib, sys, time
import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS (cambia UNO cada vez) ============================

# ---------- 1. LA RECOMPENSA: que premias y que castigas (la parte dificil del RL) ----------
# recompensa de una patada = -PESO_PRECISION*distancia_a_la_casilla + BONUS_ACIERTO*(cayo en la casilla)
#                            - PENALIZA_CAIDA*(el pato se cayo) - PESO_FUERZA*velocidad^2
PESO_PRECISION = 2.0     # AFECTA A: cuanto duele fallar por metros. Prueba 0 y ve que pasa: sin esto no sabe a donde ir.
BONUS_ACIERTO = 1.0      # AFECTA A: premia caer DENTRO de la casilla. Prueba 0 (solo premias acercarse) o 5.
PENALIZA_CAIDA = 3.0     # AFECTA A: castiga las patadas tan fuertes que tiran al pato.
PESO_FUERZA = 0.0        # AFECTA A: castiga patear fuerte. Prueba 0.5. Prediccion habitual: "ahorra y se queda corto". Medido aqui: acerto 9 de 9. ¿Por que crees que no empeoro?

# ---------- 2. EL ALGORITMO PPO ----------
ITERACIONES = 60            # AFECTA A: cuantas rondas de aprender. Mas rondas = mas tiempo y mejor (hasta un limite).
PATADAS_POR_RONDA = 12      # AFECTA A: experiencia por ronda (en el entrenamiento real son miles de robots a la vez).
                            #           Pocas = aprendizaje ruidoso; muchas = estable pero lento.
LEARNING_RATE = 0.012        # AFECTA A: el tamaño del ajuste. Muy alto (0.5) se descontrola; muy bajo (0.0005) no aprende.
CLIP = 0.2                  # AFECTA A: el limite que PPO pone a cuanto cambia la politica en cada ronda (lo que lo hace "estable").
EPOCAS = 4                  # AFECTA A: cuantas veces se reutilizan los mismos datos en cada ronda.
EXPLORACION = 0.25          # AFECTA A: cuanto prueba cosas raras al principio (desviacion de la velocidad, en m/s).
                            #           Medido aqui: 0.02 tambien saco 9 de 9 (la tarea es facil); en tareas dificiles explorar poco SI atasca.
COEF_ENTROPIA = 0.001       # AFECTA A: premio por seguir explorando (mas alto = tarda mas en decidirse).
SEMILLA = 0                 # AFECTA A: la suerte. Cambiala y repite: ¿sale igual de bien? (en RL casi nunca sale igual).

# ---------- 3. EL ENTORNO: en que mundo entrenas ----------
CASILLAS = [1, 2, 3, 4, 5, 6, 7, 8, 9]   # AFECTA A: que objetivos ve al entrenar. Prueba solo [3, 7]: ¿generaliza a las demas?
GRAVEDAD = 9.81             # AFECTA A: la fisica del mundo. 1.62 = Luna: la pelota vuela mucho mas lejos.
MASA_PELOTA = None          # AFECTA A: una pelota mas pesada llega menos lejos. Prueba 0.2 (None = la del modelo).
ROZAMIENTO_PELOTA = None    # AFECTA A: cuanto rueda tras caer. El del modelo es 0.5: con 0.25 rueda el doble, con 1.0 se queda corta.

# ---------- 4. GENERALIZAR: entrenar en mundos distintos (aleatorizacion de dominio) ----------
ALEATORIZAR = 0.0           # AFECTA A: 0 = siempre el MISMO mundo. 0.3 = en CADA patada la gravedad, la masa y el rozamiento de la
                            #           pelota cambian al azar hasta un 30 %. Una politica entrenada en un solo mundo acierta ahi...
                            #           y falla si el mundo cambia un poco. Medido: a ciegas empeora; hace falta VE_EL_MUNDO = True
                            #           (y 150 rondas) para que aguante. Compruebalo con n5_01_generalizar.py.
VE_EL_MUNDO = False         # AFECTA A: si la politica PERCIBE como es el mundo (gravedad, masa y rozamiento de la pelota) ademas de la casilla.
                            #           Con ALEATORIZAR > 0 y VE_EL_MUNDO = False entrena "a ciegas": solo aprende un promedio y falla
                            #           en todos los mundos. Con VE_EL_MUNDO = True aprende a ADAPTARSE a lo que percibe.
                            #           (En el robot real seria una estimacion: sensores, o el historial de lo que acaba de pasar.)

# Nombre con el que se guarda TU politica en la carpeta mis_politicas/. Cambialo para entrenar VARIAS y compararlas
# (n3_06_comparar_politicas.py): p. ej. "precisa" con PESO_FUERZA = 0, y "ahorradora" con PESO_FUERZA = 0.5.
NOMBRE_POLITICA = "mi_tabla_patada"
ARCHIVO_TABLA = AQUI / "mis_politicas" / f"{NOMBRE_POLITICA}.json"      # donde se guarda lo aprendido para jugar con ello

# ==========================================================================================

import patada_env  # noqa: E402  (el entorno: MuJoCo + cerebro de patada oficial)
from rayuela import board_geometry  # noqa: E402

PIES = ("kick_left", "kick_right")
VEL_MIN, VEL_MAX = 0.25, 1.8      # rango de velocidades que admite el cerebro de patada


def observacion(casilla, ctx=(0.0, 0.0, 0.0), ve_mundo=None):
    """Lo que ve la politica: donde esta la casilla y, si VE_EL_MUNDO, como es el mundo (ctx = gravedad, masa, rozamiento: 0 = normal)."""
    cx, cy = board_geometry.casilla_center(casilla)
    if VE_EL_MUNDO if ve_mundo is None else ve_mundo:
        return np.array([cx / 2.0, cy / 0.5, *ctx])
    return np.array([cx / 2.0, cy / 0.5])


class Politica:
    """Una red neuronal minima: observacion (2 o 5) -> 16 neuronas -> [velocidad media, logit del pie]. Es EL CEREBRO que se entrena."""

    def __init__(self, rng, exploracion, entradas=2):
        H = 16
        self.p = {"W1": rng.normal(0, 0.3, (H, entradas)), "b1": np.zeros(H),
                  "W2": rng.normal(0, 0.05, (2, H)), "b2": np.zeros(2),
                  "logstd": np.array([np.log(exploracion)])}
        self.m = {k: np.zeros_like(v) for k, v in self.p.items()}      # memoria de Adam
        self.v = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.t = 0

    def adelante(self, x):
        h = np.tanh(self.p["W1"] @ x + self.p["b1"])
        out = self.p["W2"] @ h + self.p["b2"]
        mu = 0.9 + 0.5 * out[0]                       # empieza patea "a 0.9 m/s" y aprende a corregirlo
        p_der = 1.0 / (1.0 + np.exp(-out[1]))         # probabilidad de usar el pie derecho
        return h, mu, p_der

    def actuar(self, x, rng, determinista=False):
        _, mu, p_der = self.adelante(x)
        std = np.exp(self.p["logstd"][0])
        if determinista:
            return mu, int(p_der > 0.5)
        return mu + std * rng.normal(), int(rng.random() < p_der)

    def logprob(self, x, v, pie):
        _, mu, p_der = self.adelante(x)
        std = np.exp(self.p["logstd"][0])
        return -0.5 * ((v - mu) / std) ** 2 - np.log(std) + (np.log(p_der + 1e-9) if pie else np.log(1 - p_der + 1e-9))

    def actualizar_ppo(self, datos, ventajas, lr, clip, epocas, coef_ent):
        """PPO: sube la probabilidad de las acciones con ventaja positiva, pero SIN cambiar la politica mas de 'clip'."""
        for _ in range(epocas):
            g = {k: np.zeros_like(v) for k, v in self.p.items()}
            for (x, v, pie, logp_viejo), A in zip(datos, ventajas):
                h, mu, p_der = self.adelante(x)
                std = np.exp(self.p["logstd"][0])
                ratio = np.exp(self.logprob(x, v, pie) - logp_viejo)
                activo = not ((A > 0 and ratio > 1 + clip) or (A < 0 and ratio < 1 - clip))   # el 'clip' de PPO
                dL = -ratio * A if activo else 0.0                                              # dPerdida/dlogp
                d_mu = dL * (v - mu) / std ** 2
                d_logstd = dL * (((v - mu) / std) ** 2 - 1) - coef_ent
                d_logit = dL * (pie - p_der)
                d_out = np.array([0.5 * d_mu, d_logit])
                g["W2"] += np.outer(d_out, h)
                g["b2"] += d_out
                d_pre = (self.p["W2"].T @ d_out) * (1 - h ** 2)
                g["W1"] += np.outer(d_pre, x)
                g["b1"] += d_pre
                g["logstd"][0] += d_logstd
            self.t += 1
            for k in self.p:                                                       # optimizador Adam
                gk = g[k] / len(datos)
                self.m[k] = 0.9 * self.m[k] + 0.1 * gk
                self.v[k] = 0.999 * self.v[k] + 0.001 * gk ** 2
                mh, vh = self.m[k] / (1 - 0.9 ** self.t), self.v[k] / (1 - 0.999 ** self.t)
                self.p[k] -= lr * mh / (np.sqrt(vh) + 1e-8)
            self.p["logstd"][0] = np.clip(self.p["logstd"][0], np.log(0.08), np.log(1.0))


def recompensa(casilla, resultado, velocidad):
    """LA RECOMPENSA. Lee esta funcion con calma: aqui esta todo lo que el robot 'quiere'."""
    x, y, cae_en, cayo = resultado
    cx, cy = board_geometry.casilla_center(casilla)
    distancia = float(np.hypot(x - cx, y - cy))
    return (-PESO_PRECISION * distancia
            + BONUS_ACIERTO * (cae_en == casilla)
            - PENALIZA_CAIDA * bool(cayo)
            - PESO_FUERZA * velocidad ** 2), distancia


def evaluar(env, pol, titulo):
    """Prueba la politica sin explorar en cada casilla y cuenta aciertos."""
    print(f"\n--- {titulo} ---\n casilla | pie     | velocidad | cayo en | error")
    aciertos, tabla = 0, {}
    for c in range(1, 10):
        v, pie = pol.actuar(observacion(c), None, determinista=True)
        v = float(np.clip(v, VEL_MIN, VEL_MAX))
        res = env.step(v, PIES[pie])
        _, d = recompensa(c, res, v)
        aciertos += res[2] == c
        tabla[c] = {"pie": PIES[pie], "velocidad": round(v, 3)}
        print(f"   {c}     | {PIES[pie][5:]:<7s} |  {v:5.2f}    |   {str(res[2]):>4s}  | {d:5.2f} m {'  <- ACIERTO' if res[2] == c else ''}")
    print(f" ACIERTOS: {aciertos} de 9")
    return aciertos, tabla


def main():
    rng = np.random.default_rng(SEMILLA)
    print("Cargando el simulador (unos segundos)...")
    env = patada_env.PatadaEnv(GRAVEDAD, MASA_PELOTA, ROZAMIENTO_PELOTA)
    pol = Politica(rng, EXPLORACION, entradas=5 if VE_EL_MUNDO else 2)
    evaluar(env, pol, "ANTES de entrenar (politica sin aprender)")

    base = {c: 0.0 for c in CASILLAS}           # "lo que se espera sacar" en cada casilla: sirve para ver si una patada fue mejor o peor
    historial, t0 = [], time.time()
    print(f"\nENTRENANDO: {ITERACIONES} rondas x {PATADAS_POR_RONDA} patadas...\n ronda | recompensa media | aciertos | exploracion | curva")
    for it in range(1, ITERACIONES + 1):
        datos, recs, hits = [], [], 0
        for _ in range(PATADAS_POR_RONDA):
            c = int(rng.choice(CASILLAS))
            ctx = (0.0, 0.0, 0.0)
            if ALEATORIZAR > 0:                 # un mundo nuevo para cada patada: asi la politica no puede "memorizar" uno
                a = ALEATORIZAR
                fg, fm, fr = (rng.uniform(1 - a, 1 + a) for _ in range(3))
                env.set_mundo(GRAVEDAD * fg, env.base_masa * fm, float(env.base_roz[0]) * fr)
                ctx = ((fg - 1) / a, (fm - 1) / a, (fr - 1) / a)         # lo que "percibe" la politica (entre -1 y 1)
            x = observacion(c, ctx)
            v, pie = pol.actuar(x, rng)
            res = env.step(float(np.clip(v, VEL_MIN, VEL_MAX)), PIES[pie])
            r, _ = recompensa(c, res, float(np.clip(v, VEL_MIN, VEL_MAX)))
            datos.append((x, v, pie, pol.logprob(x, v, pie)))
            recs.append((c, r))
            hits += res[2] == c
        for c, r in recs:
            base[c] += 0.3 * (r - base[c])
        ventaja = np.array([r - base[c] for c, r in recs])
        ventaja = (ventaja - ventaja.mean()) / (ventaja.std() + 1e-6)
        pol.actualizar_ppo(datos, ventaja, LEARNING_RATE, CLIP, EPOCAS, COEF_ENTROPIA)
        media = float(np.mean([r for _, r in recs]))
        historial.append(media)
        barra = "#" * int(max(0, (media + 4) * 6))
        print(f"  {it:3d}  |      {media:+6.2f}      |  {hits:2d}/{PATADAS_POR_RONDA}   |    {np.exp(pol.p['logstd'][0]):.2f}     | {barra}", flush=True)
    print(f"\nEntrenamiento terminado en {time.time() - t0:.0f} s.")
    env.set_mundo(GRAVEDAD, MASA_PELOTA, ROZAMIENTO_PELOTA)                       # la prueba final, en el mundo normal
    aciertos, tabla = evaluar(env, pol, "DESPUES de entrenar")
    ARCHIVO_TABLA.parent.mkdir(exist_ok=True)
    tabla["_meta"] = dict(nombre=NOMBRE_POLITICA, aciertos=int(aciertos), iteraciones=ITERACIONES, patadas_por_ronda=PATADAS_POR_RONDA,
                          learning_rate=LEARNING_RATE, exploracion=EXPLORACION, semilla=SEMILLA, casillas_entrenadas=CASILLAS,
                          recompensa=dict(precision=PESO_PRECISION, acierto=BONUS_ACIERTO, caida=PENALIZA_CAIDA, fuerza=PESO_FUERZA),
                          mundo=dict(gravedad=GRAVEDAD, masa_pelota=MASA_PELOTA, rozamiento_pelota=ROZAMIENTO_PELOTA, aleatorizar=ALEATORIZAR,
                                     ve_el_mundo=VE_EL_MUNDO))
    if VE_EL_MUNDO:                                      # esta politica necesita su red (no basta una tabla): se guarda entera
        tabla["_red"] = {k: np.asarray(v).tolist() for k, v in pol.p.items()}
    ARCHIVO_TABLA.write_text(json.dumps(tabla, indent=2), encoding="utf-8")
    print(f"\nGuardado: {ARCHIVO_TABLA.name}. Para jugar con TU politica: n4_00_partida_rayuela.py -> TABLA_PROPIA.")
    print("Ahora cambia UN parametro de arriba y compara: ¿que cambia en la curva y en los aciertos?")


if __name__ == "__main__":
    main()
