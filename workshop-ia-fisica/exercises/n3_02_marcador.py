"""NIVEL 3 - La demo con MARCADOR (para el reto "haz que falle / haz que gane").
Es la misma demo con cerebro, pero cuenta los segundos que el robot aguanta de pie
y los empujones que recibe. Una ronda dura 60 s o hasta que el robot se cae.

PUNTOS = segundos de pie (maximo 60) - empujones usados

Controles (en la TERMINAL, no en el visor):
  Flechas = velocidad | A / E = girar | Q = salir
  Ctrl + clic derecho arrastrando sobre el robot = EMPUJARLO (cuenta como 1 empujon)
Para repetir la ronda: cierra el visor (Q) y vuelve a lanzar el script.
"""
import importlib.util, os, pathlib, sys

# --- LOS CEREBROS (cambia el fichero .onnx para probar otro) ---
ANDAR  = "policies/alpha_walking.onnx"
QUIETO = "policies/alpha_stand.onnx"

# --- PERTURBACIONES: pon valores para romper el mundo (None = sin tocar) ---
VOLTAJE_BATERIA  = None   # prueba 6.5 (bateria baja). Normal: 7.4
RETRASO_MOTORES  = None   # prueba (2, 4): los motores obedecen tarde
POTENCIA_MOTORES = None   # prueba 0.7: motores mas debiles. Normal: 1.0
ROZAMIENTO_PIES  = None   # prueba 0.3: pies resbaladizos. Normal: 1.0

DURACION_RONDA = 60.0     # segundos
ALTURA_CAIDA = 0.07       # si el tronco baja de 7 cm, se ha caido (de pie ~12 cm)

root = pathlib.Path(__file__).resolve().parent.parent
os.chdir(root)
sys.path.insert(0, str(root / "scripts"))
spec = importlib.util.spec_from_file_location("infer_policy", root / "scripts" / "infer_policy.py")
ip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ip)

argv = ["infer_policy", "--walking", ANDAR, "--standing", QUIETO, "--new-cmd-obs"]
if VOLTAJE_BATERIA is not None:
    argv += ["--vin", str(VOLTAJE_BATERIA)]
if RETRASO_MOTORES is not None:
    argv += ["--delay", *map(str, RETRASO_MOTORES)]
if POTENCIA_MOTORES is not None:
    argv += ["--action-scale", str(POTENCIA_MOTORES)]
if ROZAMIENTO_PIES is not None:
    argv += ["--foot-friction", str(ROZAMIENTO_PIES)]
sys.argv = argv

import mujoco
import numpy as np

estado = dict(empujones=0, empujando=False, t0=None, siguiente_aviso=10.0, fin=False)
paso_real = mujoco.mj_step


def mj_step_con_marcador(model, data, *args, **kw):
    paso_real(model, data, *args, **kw)
    if estado["fin"]:
        return
    if estado["t0"] is None:
        estado["t0"] = data.time
    t = data.time - estado["t0"]
    # empujon = el visor aplica una fuerza externa al robot mientras arrastras con el raton
    fuerza = bool(np.any(data.xfrc_applied != 0))
    if fuerza and not estado["empujando"]:
        estado["empujones"] += 1
        print(f"  >> Empujon {estado['empujones']}")
    estado["empujando"] = fuerza
    if t >= estado["siguiente_aviso"] and t < DURACION_RONDA:
        print(f"  [marcador] {t:.0f} s de pie | {estado['empujones']} empujones")
        estado["siguiente_aviso"] += 10.0
    caido = data.qpos[2] < ALTURA_CAIDA
    if caido or t >= DURACION_RONDA:
        estado["fin"] = True
        puntos = min(t, DURACION_RONDA) - estado["empujones"]
        print("\n" + "=" * 52)
        print("  " + ("SE HA CAIDO" if caido else "AGUANTO LA RONDA ENTERA"))
        print(f"  Segundos de pie: {min(t, DURACION_RONDA):.1f}   Empujones: {estado['empujones']}")
        print(f"  PUNTOS = {puntos:.1f}")
        print("=" * 52 + "\n  (Q para salir)")




class SinRuido:
    """Quita la linea de velocidad que la demo imprime cada segundo, para que se lea el marcador."""
    def __init__(self, destino):
        self.destino = destino
    def write(self, texto):
        if "[vel 1s avg]" not in texto:
            self.destino.write(texto)
    def flush(self):
        self.destino.flush()
    def __getattr__(self, nombre):
        return getattr(self.destino, nombre)


mujoco.mj_step = mj_step_con_marcador
sys.stdout = SinRuido(sys.stdout)
print(f"Ronda de {DURACION_RONDA:.0f} s. Empuja con Ctrl + clic derecho. Q = salir.")
ip.main()
sys.stdout.flush()
os._exit(0)  # evita un 'segmentation fault' de GLFW al cerrar el visor
