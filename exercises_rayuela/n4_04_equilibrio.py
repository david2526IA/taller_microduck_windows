"""CASO DE USO 4 - EL LABORATORIO DE EQUILIBRIO: tu mueves al pato y el se autocorrige para no caerse.

Aqui no hay rayuela ni pelota: solo el Microduck de pie sobre un suelo liso y su cerebro de equilibrio (alpha_standing.onnx).
Ese cerebro no lleva una postura escrita: 50 veces por segundo MIRA su inclinacion y corrige. Para verlo, tu le
perturbas de tres maneras y el programa mide en cuanto tiempo se recupera:

   1. EMPUJONES: tecla  p  (o Ctrl + clic derecho sobre el robot, arrastrando)
   2. MOVERLE EL CUERPO: tecla  b  activa el modo "postura del cuerpo": flechas = subir/bajar y inclinar adelante/atras,
      a / e = inclinar a los lados, z / s = girar el tronco, espacio = postura neutra. Tu pides la postura;
      el cerebro mantiene el equilibrio MIENTRAS la hace.
   3. UN SUELO QUE SE MUEVE: pon PLATAFORMA = True abajo (una tabla sobre un eje, un balancin).

CONTROLES (en la TERMINAL, no en la ventana del robot):
   p = empujon (EMPUJON m/s, en direccion al azar)     b = modo postura del cuerpo     espacio = postura neutra
   flechas = andar o (en modo postura) mover el cuerpo      x = parar todo      n = NUEVA PRUEBA (el pato vuelve al inicio)      q = salir

EXPERIMENTOS: cambia UN valor, guarda (Ctrl+S), CIERRA la ventana y lanza otra vez (F5).
"""
import importlib.util, math, os, pathlib, queue, random, sys, threading, time, types
import msvcrt

for _f in (sys.stdout, sys.stderr):                  # la consola de Windows no sabe escribir la flecha del codigo oficial
    _f.reconfigure(encoding="utf-8", errors="replace")

AQUI = pathlib.Path(__file__).resolve().parent.parent

# ============================ PARAMETROS ============================

# Fuerza del empujon al pulsar p (velocidad que se le da al tronco, m/s, en direccion al azar).
#   AFECTA A: lo cerca que esta de caerse. Busca su limite. Medido en este simulador: 0.4 se recupera siempre (en ~0,5-0,9 s);
#   0.6 casi siempre; 0.8 ya falla a veces, segun la direccion. Con retraso o bateria baja el limite baja.
EMPUJON = 0.4

# Bateria (voltios). 7.4 = llena | 6.5 = baja.
#   AFECTA A: la fuerza de los motores: con bateria baja corrige peor.
VOLTAJE_BATERIA = 7.4

# Retraso de los motores en pasos de control de 20 ms: None = ninguno | 2 = 40 ms | (2, 4) = entre 40 y 80 ms.
#   AFECTA A: el cerebro reacciona sobre lo que veia hace un instante. Con retraso, corregir se vuelve mucho mas dificil.
RETRASO_MOTORES = None

# Potencia de los motores (1.0 = normal | 0.7 = un 30 % mas debiles).
#   AFECTA A: cuanto puede corregir en cada paso.
POTENCIA_MOTORES = 1.0

# Rozamiento del suelo (None = el del modelo | 0.2 = hielo | 2.0 = goma).
#   AFECTA A: en el hielo los pies resbalan y el empujon se convierte en un patinazo.
ROZAMIENTO = None

# Cerebros (ficheros .onnx de rayuela-oficial/policies-v1): el de equilibrio quieto y el de andar.
#   AFECTA A: lo que sabe hacer. Cambia a otro cerebro y compara como aguanta el mismo empujon.
CEREBRO_QUIETO = "alpha_standing.onnx"
CEREBRO_ANDAR = "alpha_walking.onnx"

# ---- Suelo que se mueve: una tabla sobre un eje (balancin) ----
# Ponlo en True para que el pato se suba a una tabla que se inclina.
PLATAFORMA = False
INCLINACION_MAX = 8        # grados de balanceo a cada lado
RIGIDEZ_MUELLE = 3.0       # fuerza que devuelve la tabla a la horizontal. 3.0 = facil | 0.3 = muy dificil | 0 = tabla libre
AMORTIGUACION = 0.3        # freno del balanceo: mas alto = la tabla se mueve mas despacio
MASA_TABLA = 0.2           # kg

# ====================================================================

ALTO_EJE, GROSOR = 0.065, 0.02            # altura del centro de la tabla y grosor (m)

for _n in ("termios", "tty"):                # Windows no tiene termios/tty: se sustituye el modulo, no el repo oficial
    sys.modules.setdefault(_n, types.ModuleType(_n))
sys.modules["tty"].setcbreak = lambda *a, **k: None

OFICIAL = AQUI / "rayuela-oficial"
os.chdir(OFICIAL)
sys.path.insert(0, str(OFICIAL / "scripts"))
import mujoco  # noqa: E402
import numpy as np  # noqa: E402

spec_ip = importlib.util.spec_from_file_location("infer_policy", OFICIAL / "scripts" / "infer_policy.py")
ip = importlib.util.module_from_spec(spec_ip)
spec_ip.loader.exec_module(ip)

REINICIAR, EMPUJAR = threading.Event(), threading.Event()


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
            elif ch.lower() == "p":            # el empujon lo da ESTE programa (con la fuerza EMPUJON), no el oficial
                EMPUJAR.set()
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

# ---- el suelo que se mueve (si se pide): se anade una tabla con bisagra al cargar la escena oficial ----
if PLATAFORMA:
    _from_file = mujoco.MjSpec.from_file

    def _con_plataforma(*a, **k):
        spec = _from_file(*a, **k)
        tabla = spec.worldbody.add_body(name="balancin", pos=[0, 0, ALTO_EJE])
        tabla.add_joint(name="balancin_bisagra", type=mujoco.mjtJoint.mjJNT_HINGE, axis=[0, 1, 0], limited=True,
                        range=[-math.radians(INCLINACION_MAX), math.radians(INCLINACION_MAX)],
                        stiffness=RIGIDEZ_MUELLE, damping=AMORTIGUACION)
        tabla.add_geom(name="balancin_tabla", type=mujoco.mjtGeom.mjGEOM_BOX, size=[0.25, 0.15, GROSOR / 2],
                       mass=MASA_TABLA, friction=[1.0, 0.005, 0.0001], rgba=[0.75, 0.55, 0.3, 1])
        spec.worldbody.add_geom(name="balancin_eje", type=mujoco.mjtGeom.mjGEOM_CYLINDER, size=[0.02, 0.15, 0],
                                euler=[math.pi / 2, 0, 0], pos=[0, 0, ALTO_EJE - 0.03], rgba=[0.3, 0.3, 0.3, 1],
                                contype=0, conaffinity=0)
        return spec
    mujoco.MjSpec.from_file = staticmethod(_con_plataforma)

# ---- lo que se mide y lo que se hace en cada paso de la simulacion ----
estado = {"policy": None, "snap": None, "push": None, "ultimo": 0.0}
_init_original = ip.PolicyInference.__init__


def _init_capturando(self, *a, **k):
    _init_original(self, *a, **k)
    estado["policy"] = self


ip.PolicyInference.__init__ = _init_capturando
_paso_real = mujoco.mj_step


def _inclinacion(model, data):
    """Grados que se ha inclinado el tronco respecto a la vertical."""
    r = data.xmat[model.body("trunk_base").id]
    return math.degrees(math.acos(max(-1.0, min(1.0, r[8]))))


def _paso(model, data, *a, **k):
    adr = model.jnt_dofadr[model.joint("trunk_base_freejoint").id]
    if estado["snap"] is None:
        if PLATAFORMA:                                         # el pato empieza SOBRE la tabla
            qa = model.jnt_qposadr[model.joint("trunk_base_freejoint").id]
            data.qpos[qa + 2] += ALTO_EJE + GROSOR / 2
            mujoco.mj_forward(model, data)
        estado["snap"] = (data.qpos.copy(), data.qvel.copy())
        print(f"\nListo. Pulsa p para empujarlo ({EMPUJON} m/s), b para moverle el cuerpo, n para reiniciar.\n", flush=True)
    elif REINICIAR.is_set():
        REINICIAR.clear()
        p = estado["policy"]
        data.qpos[:], data.qvel[:] = estado["snap"]
        data.ctrl[:] = 0
        estado["push"] = None
        if p is not None:
            p.set_vel_cmd(0.0, 0.0, 0.0)
            p.body_cmd[:] = 0
            if getattr(p, "bam_ctrl", None) is not None:
                p.bam_ctrl.reset(data.qpos)
        print("\n>> NUEVA PRUEBA: el pato vuelve al inicio\n", flush=True)
    elif EMPUJAR.is_set():
        EMPUJAR.clear()
        ang = random.uniform(0, 2 * math.pi)
        data.qvel[adr + 0] = EMPUJON * math.cos(ang)
        data.qvel[adr + 1] = EMPUJON * math.sin(ang)
        estado["push"] = dict(t0=data.time, max=0.0, calmo=0, dir=math.degrees(ang))
        print(f"EMPUJON de {EMPUJON} m/s (direccion {math.degrees(ang):.0f}°)...", flush=True)
    _paso_real(model, data, *a, **k)
    pu = estado["push"]                                       # medir cuanto tarda en recuperarse
    if pu is not None:
        inc = _inclinacion(model, data)
        pu["max"] = max(pu["max"], inc)
        pu["calmo"] = pu["calmo"] + 1 if inc < 3.0 else 0
        z = data.xpos[model.body("trunk_base").id][2]
        if inc > 60 or z < 0.07 + (ALTO_EJE + GROSOR / 2 if PLATAFORMA else 0):
            print(f"   -> SE HA CAIDO (inclinacion maxima {pu['max']:.0f}°). Prueba un empujon mas suave.", flush=True)
            estado["push"] = None
        elif pu["calmo"] >= 40 and data.time - pu["t0"] > 0.2:          # 40 pasos de 5 ms = 0,2 s estable
            print(f"   -> RECUPERADO en {data.time - pu['t0'] - 0.2:.2f} s (inclinacion maxima {pu['max']:.0f}°)", flush=True)
            estado["push"] = None
        elif data.time - pu["t0"] > 6.0:
            print(f"   -> sigue tambaleandose tras 6 s (inclinacion maxima {pu['max']:.0f}°)", flush=True)
            estado["push"] = None


mujoco.mj_step = _paso

P = str(OFICIAL / "policies-v1") + os.sep
argv = ["infer_policy", "--new-cmd-obs", "--walking", P + CEREBRO_ANDAR, "--standing", P + CEREBRO_QUIETO,
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
