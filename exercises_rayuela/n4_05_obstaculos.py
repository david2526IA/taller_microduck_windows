"""CASO DE USO 5 - EL CIRCUITO DE OBSTACULOS (inspirado en la demo de NVIDIA del GTC Berlin 2026).

En el GTC de Berlin, NVIDIA monto un circuito de obstaculos para el Microduck: un agente de IA construye la escena en Isaac Sim,
se afina una politica de andar con 4.096 robots en una GPU (Isaac Lab) y se valida midiendo obstaculos superados, caidas y colisiones.
Aqui haces la parte que cabe en un PC sin GPU, en MuJoCo: describes el circuito con codigo, eliges el cerebro, lo ves andar
y lo validas. Lo que no se replica: el agente que construye la escena, la camara de profundidad, Isaac Sim y el entrenamiento en GPU.

EN CRESCENDO: sube NIVEL de 0 a 4. Cada nivel anade UNA cosa y el circuito mide siempre lo mismo (meta a 4,9 m):
   0 llano (la referencia) | 1 + rampa | 2 + escalones | 3 + cuadricula irregular | 4 + escombros
Y prueba los tres cerebros, del menos al mas entrenado en terreno irregular:
   alpha_walking (entrenado en llano) | rough_walk_e (afinado en terreno hostil) | rough_walk_g (entrenado desde cero en terreno irregular)

CONTROLES (en la TERMINAL, no en la ventana del robot):
   el pato echa a andar solo (AVANCE_AUTOMATICO) | flechas = andar, girar, frenar | espacio = parar | x = parar todo
   n = REINTENTAR desde la salida | q = salir | Ctrl + clic derecho sobre el robot = empujarlo
El programa avisa al entrar en cada seccion, cuando se cae (y donde) y cuando llega a la meta.

EXPERIMENTOS: cambia UN valor, guarda (Ctrl+S), CIERRA la ventana y lanza otra vez (F5). Para comparar cerebros con numeros,
usa n4_06_validar_politicas.py.
"""
import importlib.util, math, os, pathlib, queue, sys, threading, time, types
import msvcrt

for _f in (sys.stdout, sys.stderr):                  # la consola de Windows no sabe escribir la flecha del codigo oficial
    _f.reconfigure(encoding="utf-8", errors="replace")

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# El crescendo: cuantas cosas se activan (0 = llano ... 4 = rampa + escalones + cuadricula + escombros).
#   AFECTA A: lo dificil que es el circuito. Empieza en 0 y ve subiendo: ¿en que nivel se cae cada cerebro?
NIVEL = 2

# El cerebro de andar: "alpha_walking", "rough_walk_e" o "rough_walk_g" (o la ruta a un .onnx tuyo).
#   AFECTA A: lo que ha aprendido. Los dos rough_walk (Hugging Face, Apache-2.0) se entrenaron con terreno irregular.
CEREBRO = "alpha_walking"

# Velocidad de avance que se le pide al arrancar (m/s, 0 a 0.4; el pato real avanza a unos 0,15 m/s con 0.4). 0 = no echa a andar solo (lo llevas tu con las flechas).
#   AFECTA A: andar mas rapido hace tropezar mas con los obstaculos.
AVANCE_AUTOMATICO = 0.4

# ¿Corrige el rumbo para ir recto? Cada cerebro se desvia a su manera (alpha_walking acaba andando en un arco enorme).
#   AFECTA A: con True el pato mira siempre hacia la meta (como la orden de "heading" de NVIDIA). Con False lo conduces tu con
#   las flechas y ves la desviacion natural de cada cerebro.
MANTENER_RUMBO = True

# ---- El circuito (metros y grados). Lo que se describe en crear_circuito(), en windows/obstaculos.py ----
ANGULO_RAMPA = 6.0          # nivel 1+. La bateria de Pollen llega a 9 grados; NVIDIA usa pendientes del 3 al 10 %.
N_ESCALONES = 3             # nivel 2+: cuantos escalones sube (y baja)
ALTURA_ESCALON = 0.010      # nivel 2+: 1 cm. NVIDIA entrena de 0 a 1,5 cm. Los rough_walk fallan al bajar escalones de 2 cm o mas.
ALTURA_CUADRICULA = 0.010   # nivel 3+: baldosas con altura al azar entre 0 y este valor
ALTURA_ESCOMBROS = 0.015    # nivel 4+: bultos al azar entre 0,2 cm y este valor
SEMILLA_CIRCUITO = 0        # cambia el azar de baldosas y escombros: ¿sigue aguantando?

# ====================================================================

CFG = dict(nivel=NIVEL, angulo_rampa=ANGULO_RAMPA, n_escalones=N_ESCALONES, altura_escalon=ALTURA_ESCALON,
           altura_cuadricula=ALTURA_CUADRICULA, altura_escombros=ALTURA_ESCOMBROS, semilla=SEMILLA_CIRCUITO)

import obstaculos  # noqa: E402  (el circuito y su validacion)

ip = obstaculos._cargar_oficial()                       # el script oficial infer_policy.py, sin modificar
import mujoco  # noqa: E402

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
            else:
                self._cola.put(ch.lower() if ch.isalpha() else ch)

    def get_keys(self):
        teclas = []
        while True:
            try:
                teclas.append(self._cola.get_nowait())
            except queue.Empty:
                return teclas


ip.TerminalInput = TecladoWindows

# el circuito se anade a la escena oficial al cargarla (el cargador oficial abre el XML con MjSpec)
_from_file = mujoco.MjSpec.from_file
mujoco.MjSpec.from_file = staticmethod(lambda *a, **k: obstaculos.crear_circuito(_from_file(*a, **k), **CFG))

estado = {"policy": None, "snap": None, "seccion": None, "fin": False, "t0": 0.0, "n": 0}
_init_original = ip.PolicyInference.__init__


def _init_capturando(self, *a, **k):
    _init_original(self, *a, **k)
    estado["policy"] = self


ip.PolicyInference.__init__ = _init_capturando
_paso_real = mujoco.mj_step


def _paso(model, data, *a, **k):
    if estado["snap"] is None:
        estado["snap"] = (data.qpos.copy(), data.qvel.copy())
        if AVANCE_AUTOMATICO and estado["policy"] is not None:
            estado["policy"].set_vel_cmd(AVANCE_AUTOMATICO, 0.0, 0.0)
        estado["t0"] = data.time
        print(f"\nCircuito nivel {NIVEL} ({obstaculos.NIVELES[NIVEL]}) con el cerebro {CEREBRO}. Meta a {obstaculos.X_FIN} m.\n", flush=True)
    elif REINICIAR.is_set():
        REINICIAR.clear()
        p = estado["policy"]
        data.qpos[:], data.qvel[:] = estado["snap"]
        data.ctrl[:] = 0
        estado.update(seccion=None, fin=False, t0=data.time)
        if p is not None:
            p.set_vel_cmd(AVANCE_AUTOMATICO or 0.0, 0.0, 0.0)
            if getattr(p, "bam_ctrl", None) is not None:
                p.bam_ctrl.reset(data.qpos)
        print("\n>> OTRO INTENTO desde la salida\n", flush=True)
    _paso_real(model, data, *a, **k)
    if estado["fin"]:
        return
    cuerpo = model.body("trunk_base").id
    estado["n"] += 1
    if MANTENER_RUMBO and AVANCE_AUTOMATICO and estado["policy"] is not None and estado["n"] % 20 == 0:
        estado["policy"].set_vel_cmd(AVANCE_AUTOMATICO, 0.0, obstaculos.rumbo_wz(data, cuerpo))
    x = float(data.xpos[cuerpo][0])
    sec = obstaculos.seccion_en(x)
    if sec != estado["seccion"]:
        estado["seccion"] = sec
        if sec not in ("llano",):
            print(f"  -> {sec.upper()}  (x = {x:.1f} m)", flush=True)
    tilt = math.degrees(math.acos(max(-1.0, min(1.0, data.xmat[cuerpo][8]))))
    if tilt > 55 or data.xpos[cuerpo][2] < 0.05:
        estado["fin"] = True
        print(f"\n   SE HA CAIDO en la seccion {obstaculos.seccion_en(x).upper()} (x = {x:.2f} m, a los {data.time - estado['t0']:.1f} s). "
              f"Pulsa n para reintentar o sube de cerebro.\n", flush=True)
    elif x >= obstaculos.X_FIN:
        estado["fin"] = True
        print(f"\n   *** META ALCANZADA en {data.time - estado['t0']:.1f} s con {CEREBRO} (nivel {NIVEL}) ***\n", flush=True)


mujoco.mj_step = _paso

ruta = pathlib.Path(CEREBRO) if os.path.exists(str(CEREBRO)) else obstaculos.CEREBROS[CEREBRO]
oficial = obstaculos.OFICIAL / "policies-v1"
sys.argv = ["infer_policy", "--new-cmd-obs", "--walking", str(ruta), "--standing", str(oficial / "alpha_standing.onnx")]

if __name__ == "__main__":
    print(__doc__)
    ip.main()
    sys.stdout.flush()
    os._exit(0)
