"""CASO DE USO 2 - EL MICRODUCK SOBRE PATINES (misma interfaz que la Rayuela).

Es el MISMO robot con otro CUERPO (ruedas bajo los pies) y otro CEREBRO (roller.onnx), entrenado con la misma receta.
Sirve para ver que cambiando cuerpo + cerebro + recompensa sale una habilidad nueva sin tocar el simulador.
Corre el script oficial scripts/infer_policy.py de rayuela-oficial/ sin modificarlo.

CONTROLES (en la TERMINAL, no en la ventana del robot):
   flecha arriba = empujar (acelerar)    flecha abajo = frenar     espacio = dejar de pedir velocidad (rodar)
   flechas izq / dcha  o  a / e = girar  x = parar todo            q = salir
   p = EMPUJON aleatorio (para probar el equilibrio)               ctrl + clic derecho sobre el robot = empujarlo
   n = NUEVA PARTIDA: el pato vuelve al punto de partida (anadido para Windows)

EXPERIMENTOS: cambia UN valor de la lista de abajo, guarda, CIERRA la ventana y lanza otra vez.
"""
import os, pathlib, sys, threading, time, types, queue
import msvcrt

# La consola de Windows no sabe escribir la flecha del codigo oficial: se fuerza UTF-8.
for _f in (sys.stdout, sys.stderr):
    _f.reconfigure(encoding="utf-8", errors="replace")

AQUI = pathlib.Path(__file__).resolve().parent.parent

# ============================ PARAMETROS ============================

# Bateria (voltios). 7.4 = llena | 6.5 = baja.
#   AFECTA A: la fuerza de los motores. Con bateria baja las ruedas empujan menos y el equilibrio se complica.
VOLTAJE_BATERIA = 7.4

# Retraso de los motores, en pasos de control de 20 ms: None = ninguno | 2 = 40 ms | (2, 4) = entre 40 y 80 ms.
#   AFECTA A: el cerebro reacciona sobre lo que veia hace un instante. Con retraso, el equilibrio sobre patines se vuelve muy dificil.
RETRASO_MOTORES = None

# Potencia de los motores (1.0 = normal | 0.7 = un 30 % mas debiles).
#   AFECTA A: cuanto responde el pato a cada orden del cerebro.
POTENCIA_MOTORES = 1.0

# Rozamiento del suelo (None = el del modelo | 0.2 = hielo | 2.0 = goma).
#   AFECTA A: cuanto agarran las ruedas. En hielo se desliza sin control.
ROZAMIENTO = None

# Cerebros (ficheros .onnx de workshop-ia-fisica/policies): el que rueda y el que se agacha quieto.
#   AFECTA A: lo que sabe hacer. Cambia a otro cerebro y mira.
CEREBRO_RODAR = "roller.onnx"
CEREBRO_QUIETO = "roller_crouch.onnx"

# ====================================================================

# --- Windows no tiene termios/tty: se sustituye el modulo, no el repo oficial ---
for _n in ("termios", "tty"):
    sys.modules.setdefault(_n, types.ModuleType(_n))
sys.modules["tty"].setcbreak = lambda *a, **k: None

OFICIAL = AQUI / "rayuela-oficial"
POLITICAS = AQUI / "workshop-ia-fisica" / "policies"
os.chdir(OFICIAL)
sys.path.insert(0, str(OFICIAL / "scripts"))
import importlib.util
import mujoco  # noqa: E402

spec = importlib.util.spec_from_file_location("infer_policy", OFICIAL / "scripts" / "infer_policy.py")
ip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ip)

REINICIAR = threading.Event()


class TecladoWindows:
    _FLECHAS = {"H": "up", "P": "down", "M": "right", "K": "left"}

    def __init__(self):
        self._cola = queue.Queue()
        self.enabled = sys.stdin.isatty()
        self._parar = threading.Event()

    def __enter__(self):
        if self.enabled:
            threading.Thread(target=self._leer, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self._parar.set()

    def _leer(self):
        while not self._parar.is_set():
            if not msvcrt.kbhit():
                time.sleep(0.02)
                continue
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):
                n = self._FLECHAS.get(msvcrt.getwch())
                if n:
                    self._cola.put(n)
                continue
            if ch.lower() == "n":
                REINICIAR.set()
                continue
            self._cola.put(ch.lower() if ch.isalpha() else ch)

    def get_keys(self):
        teclas = []
        while True:
            try:
                teclas.append(self._cola.get_nowait())
            except queue.Empty:
                return teclas


ip.TerminalInput = TecladoWindows

# --- boton "nueva partida": se captura el cerebro y el estado inicial, y se restauran al pulsar n ---
estado = {"policy": None, "snap": None}
_init_original = ip.PolicyInference.__init__


def _init_capturando(self, *a, **k):
    _init_original(self, *a, **k)
    estado["policy"] = self


ip.PolicyInference.__init__ = _init_capturando
_paso_real = mujoco.mj_step


def _paso(model, data, *a, **k):
    if estado["snap"] is None:
        estado["snap"] = (data.qpos.copy(), data.qvel.copy())
    elif REINICIAR.is_set():
        REINICIAR.clear()
        p = estado["policy"]
        data.qpos[:], data.qvel[:] = estado["snap"]
        data.ctrl[:] = 0
        if p is not None:
            p.set_vel_cmd(0.0, 0.0, 0.0)
            if getattr(p, "bam_ctrl", None) is not None:
                p.bam_ctrl.reset(data.qpos)
        print("\n>> NUEVA PARTIDA: el pato vuelve al punto de partida\n", flush=True)
    _paso_real(model, data, *a, **k)


mujoco.mj_step = _paso

argv = ["infer_policy", "--roller", "--new-cmd-obs",
        "--walking", str(POLITICAS / CEREBRO_RODAR), "--standing", str(POLITICAS / CEREBRO_QUIETO),
        "--vin", str(VOLTAJE_BATERIA), "--action-scale", str(POTENCIA_MOTORES)]
if RETRASO_MOTORES is not None:
    argv += ["--delay", *map(str, [RETRASO_MOTORES] if isinstance(RETRASO_MOTORES, int) else RETRASO_MOTORES)]
if ROZAMIENTO is not None:
    argv += ["--foot-friction", str(ROZAMIENTO)]
sys.argv = argv

if __name__ == "__main__":
    print(__doc__)
    ip.main()
    sys.stdout.flush()
    os._exit(0)
