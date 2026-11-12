"""CASOS DE USO del Microduck en Windows, con la MISMA arquitectura que la Rayuela oficial de Bravo Robots.

El repo oficial (rayuela-oficial/) se usa SIN modificar: simulacion MuJoCo + motores BAM + cerebros ONNX,
y los nodos vision_node, control_node y teleop_keyboard. Lo unico que cambia es que ROS 2 (que exige Ubuntu)
se sustituye por un "ROS 2 en miniatura" (windows/ros_shim/) que corre dentro de un solo proceso.

    python windows\\casos.py rayuela        # la rayuela: patear la pelota a una casilla
    (patines y cuerda: proximamente, con esta misma interfaz)

TECLAS (se pulsan en la TERMINAL, no en la ventana del robot) - las mismas que el teleop oficial:
    flechas = andar / girar      espacio = poner la velocidad a cero      x = parar todo
    1-9, 0  = patada a la casilla 1-9 (0 = cielo)      k / l = patada pie izquierdo / derecho
    r = voltereta   y = sentarse / levantarse   g = recoger del suelo
    h = IR A CASA (el pato camina solo hasta el punto de partida)       q = salir
    n = NUEVA PARTIDA: reinicia el entorno (pato y pelota en su sitio)  [anadido para Windows]
Ctrl + clic derecho arrastrando sobre el robot = empujarlo.
Tras una patada, la vision detecta en que casilla cae la pelota y el control lleva al pato hasta ella.
"""
import argparse, os, pathlib, queue, sys, threading, time, types
import msvcrt

# La consola de Windows (cp1252) no sabe escribir la flecha "→" del codigo oficial: se fuerza UTF-8.
for _f in (sys.stdout, sys.stderr):
    _f.reconfigure(encoding="utf-8", errors="replace")

AQUI = pathlib.Path(__file__).resolve().parent.parent
OFICIAL = AQUI / "rayuela-oficial"
if not (OFICIAL / "scripts" / "infer_policy.py").exists():
    raise SystemExit("Falta rayuela-oficial/. Ejecuta antes clonar_todo.ps1")

# --- Windows no tiene termios/tty (el teclado oficial es de Linux): se sustituye el modulo, no el repo ---
for _n in ("termios", "tty"):
    sys.modules.setdefault(_n, types.ModuleType(_n))
sys.modules["tty"].setcbreak = lambda *a, **k: None
os.environ["MICRODUCK_RL_ROOT"] = str(OFICIAL)
os.chdir(OFICIAL)
sys.path.insert(0, str(OFICIAL / "scripts"))
sys.path.insert(0, str(OFICIAL / "ros2_microduck" / "src" / "rayuela"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "ros_shim"))      # "ROS 2 en miniatura"

import mujoco  # noqa: E402
import rclpy  # noqa: E402  (la version miniatura)
from rclpy.node import Node  # noqa: E402
from rclpy.qos import QoSDurabilityPolicy, QoSProfile  # noqa: E402
from geometry_msgs.msg import PoseStamped, Twist  # noqa: E402
from sensor_msgs.msg import CameraInfo, Image  # noqa: E402
from std_msgs.msg import Header, String  # noqa: E402

from rayuela import rayuela_ipc as ipc, ros_utils, sim_setup, sim_worker  # noqa: E402  (codigo oficial)
from rayuela import control_node, teleop_keyboard, vision_node  # noqa: E402  (codigo oficial)


class Puente(Node):
    """Hace lo que bridge_node.py oficial: conecta la simulacion con los topicos. Aqui sin socket: va en el mismo proceso."""

    def __init__(self, mundo):
        super().__init__("rayuela_bridge_node")
        self.mundo = mundo
        latched = QoSProfile(depth=1, durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)
        self.image_pub = self.create_publisher(Image, "/rayuela/angled_camera/image_raw", 10)
        self.camera_info_pub = self.create_publisher(CameraInfo, "/rayuela/angled_camera/camera_info", latched)
        self.pose_pub = self.create_publisher(PoseStamped, "/rayuela/duck_pose", 10)
        self.policy_pub = self.create_publisher(String, "/rayuela/current_policy", 10)
        self.camera_info_pub.publish(ros_utils.camera_info_msg())
        self.create_subscription(Twist, "/rayuela/cmd_vel", self._on_cmd_vel, 10)
        self.create_subscription(String, "/rayuela/behavior_cmd", self._on_behavior, 10)

    # simulacion -> topicos
    def desde_sim(self, tipo, cuerpo):
        ahora = self.get_clock().now().to_msg()
        if tipo == ipc.MSG_POSE:
            _, x, y, z, qx, qy, qz, qw = ipc.unpack_pose(cuerpo)
            self.pose_pub.publish(ros_utils.pose_msg(ahora, x, y, z, qx, qy, qz, qw))
        elif tipo == ipc.MSG_POLICY_STATE:
            self.policy_pub.publish(String(data=ipc.unpack_policy_state(cuerpo)))
        elif tipo == ipc.MSG_IMAGE:
            cam, _, w, h, rgb = ipc.unpack_image(cuerpo)
            if cam == ipc.CAM_ANGLED:
                self.image_pub.publish(ros_utils.rgb8_image_msg(rgb, w, h, Header(stamp=ahora, frame_id="angled_cam")))

    # topicos -> simulacion
    def _on_cmd_vel(self, msg):
        self.mundo._vel_gate.apply(msg.linear.x, msg.linear.y, msg.angular.z)

    def _on_behavior(self, msg):
        self.mundo._on_behavior(msg.data.strip())


class Mundo(sim_worker.SimWorker):
    """El SimWorker oficial, con el socket de ROS sustituido por el Puente en memoria y un boton de nueva partida."""

    def __init__(self, *a, segundos=None, **k):
        super().__init__(*a, **k)
        self._snap = (self.data.qpos.copy(), self.data.qvel.copy())
        self.puente = None
        self.reiniciar = False
        self.t0, self.segundos = time.time(), segundos

    def connect(self): pass

    def _send(self, tipo, cuerpo):
        if self.puente is not None:
            self.puente.desde_sim(tipo, cuerpo)

    def nueva_partida(self):
        self.policy.stop_all()
        self.data.qpos[:], self.data.qvel[:] = self._snap
        self.data.ctrl[:] = 0
        self._vel_gate._last_key = None
        self._vel_gate.apply(0.0, 0.0, 0.0)
        self.bam_ctrl.reset(self.data.qpos)
        self.policy.set_position_targets(self.policy.default_pose)
        mujoco.mj_forward(self.model, self.data)
        print("\n>> NUEVA PARTIDA: pato y pelota en su sitio\n", flush=True)

    def _update_status(self):
        """Se llama una vez por paso de control: aqui se atienden cosas que piden otros hilos."""
        if self.reiniciar:
            self.reiniciar = False
            self.nueva_partida()
        if not rclpy.ok() or (self.segundos and time.time() - self.t0 > self.segundos):
            raise KeyboardInterrupt
        super()._update_status()


class TecladoWindows:
    """Sustituye al TerminalInput de Linux del teleop oficial: lee teclas en la consola de Windows."""
    _FLECHAS = {"H": "up", "P": "down", "M": "right", "K": "left"}
    mundo = None

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
                nombre = self._FLECHAS.get(msvcrt.getwch())
                if nombre:
                    self._cola.put(nombre)
                continue
            if ch.lower() == "n" and TecladoWindows.mundo is not None:     # tecla anadida: nueva partida
                TecladoWindows.mundo.reiniciar = True
                continue
            self._cola.put(ch.lower() if ch.isalpha() else ch)

    def get_keys(self):
        teclas = []
        while True:
            try:
                teclas.append(self._cola.get_nowait())
            except queue.Empty:
                return teclas


def clase_nodo(modulo):
    return next(c for c in vars(modulo).values()
                if isinstance(c, type) and issubclass(c, Node) and c is not Node and c.__module__ == modulo.__name__)


def hilo_nodo(fabrica, nombre):
    """Lo que hace ros_utils.spin_node del repo oficial, pero en un hilo (aqui todo vive en un proceso)."""
    def correr():
        nodo = fabrica()
        try:
            rclpy.spin(nodo)
        except Exception as e:
            print(f"[{nombre}] ERROR: {e!r}", flush=True)
            raise
        finally:
            nodo.destroy_node()
    t = threading.Thread(target=correr, daemon=True, name=nombre)
    t.start()
    return t


class Marcador(Node):
    """Cuenta puntos: se suscribe a /rayuela/target_casilla (donde la VISION dice que ha caido la pelota)."""

    def __init__(self, objetivo, puntos):
        super().__init__("rayuela_marcador")
        from rayuela_msgs.msg import TargetCasilla
        self.puntos_tabla, self.total, self.ronda = puntos, 0, 0
        self.objetivo_fijo = objetivo
        self.nueva_ronda()
        self.create_subscription(TargetCasilla, "/rayuela/target_casilla", self._on_casilla, 10)

    def nueva_ronda(self):
        import random
        self.ronda += 1
        self.objetivo = random.randint(1, 9) if self.objetivo_fijo in (None, "aleatorio") else int(self.objetivo_fijo)
        print(f"=== RONDA {self.ronda}: mete la pelota en la CASILLA {self.objetivo}  (puntos totales: {self.total}) ===",
              flush=True)

    def _on_casilla(self, msg):
        dist = abs(msg.casilla_id - self.objetivo)
        ganados = self.puntos_tabla.get(min(dist, 2), 0)
        self.total += ganados
        veredicto = "ACIERTO" if dist == 0 else ("casi" if dist == 1 else "fallo")
        print(f"  >> cayo en la casilla {msg.casilla_id} ({veredicto}): +{ganados} puntos. TOTAL = {self.total}", flush=True)


class Monitor(Node):
    """Un nodo que SOLO escucha: se suscribe a todos los topicos de la Rayuela y cada 'cada' segundos imprime
    cuantos mensajes por segundo llegan por cada uno y el ultimo valor. Es lo que en ROS 2 real haria 'ros2 topic hz'."""

    TOPICOS = {
        "/rayuela/cmd_vel": "Twist  (velocidad pedida al pato)",
        "/rayuela/behavior_cmd": "String (patada, voltereta, parar...)",
        "/rayuela/go_home": "Bool   (volver a casa)",
        "/rayuela/duck_pose": "PoseStamped (donde esta el pato)",
        "/rayuela/current_policy": "String (que cerebro manda ahora)",
        "/rayuela/angled_camera/image_raw": "Image  (lo que ve la camara)",
        "/rayuela/target_casilla": "TargetCasilla (donde cayo la pelota)",
    }

    def __init__(self, cada=3.0):
        super().__init__("rayuela_monitor")
        import time as _t
        self.cuenta = {t: 0 for t in self.TOPICOS}
        self.ultimo = {t: "-" for t in self.TOPICOS}
        self.t0, self.cada = _t.monotonic(), cada
        for t in self.TOPICOS:
            self.create_subscription(object, t, lambda m, t=t: self._on(t, m), 10)
        self.create_timer(cada, self._imprimir)

    def _on(self, t, m):
        self.cuenta[t] += 1
        if t == "/rayuela/duck_pose":
            p = m.pose.position
            self.ultimo[t] = f"x={p.x:+.2f} y={p.y:+.2f}"
        elif t == "/rayuela/cmd_vel":
            self.ultimo[t] = f"vx={m.linear.x:+.2f} giro={m.angular.z:+.2f}"
        elif t == "/rayuela/angled_camera/image_raw":
            self.ultimo[t] = f"{m.width}x{m.height}"
        elif t == "/rayuela/target_casilla":
            self.ultimo[t] = f"casilla {m.casilla_id}"
        else:
            self.ultimo[t] = str(getattr(m, "data", m))

    def _imprimir(self):
        print(f"\n--- ROS 2 EN VIVO (cada {self.cada:.0f} s) ---  topico  |  msg/s  |  ultimo valor", flush=True)
        for t, desc in self.TOPICOS.items():
            print(f"  {t:<36s} {self.cuenta[t] / self.cada:6.1f}   {self.ultimo[t]:<26s} {desc}", flush=True)
            self.cuenta[t] = 0


def hilo_teleop(guion, velocidad_patada=None, marcador=None, tabla=None):
    """El bucle de teleop_keyboard.main() oficial; con --auto, las teclas vienen de un guion en vez del teclado."""
    def correr():
        nodo = teleop_keyboard.RayuelaTeleopKeyboard()
        t0 = time.time()
        guion_ = sorted(guion or [])

        def tecla_a_accion(tecla):
            if tecla == "n":                                   # nueva partida (anadida para Windows)
                TecladoWindows.mundo.reiniciar = True
                if marcador:
                    marcador.nueva_ronda()
            elif tabla and tecla.isdigit() and str(10 if tecla == "0" else int(tecla)) in tabla:
                # 1-9: patada segun TU tabla (la que entrenaste en n3_05), en vez de la tabla oficial
                e = tabla[str(10 if tecla == "0" else int(tecla))]
                nodo.behavior_pub.publish(String(data=f"{e['pie']}:{e['velocidad']}"))
                print(f"Casilla {tecla}: TU politica elige {e['pie']} a {e['velocidad']} m/s", flush=True)
            elif velocidad_patada and tecla in ("k", "l"):     # patada con la velocidad que TU eliges
                pie = "kick_left" if tecla == "k" else "kick_right"
                nodo.behavior_pub.publish(String(data=f"{pie}:{velocidad_patada}"))
                print(f"Patada {pie} a {velocidad_patada} m/s", flush=True)
            else:
                return nodo.handle_key(tecla)
            return True

        with TecladoWindows() as term:
            while rclpy.ok():
                rclpy.spin_once(nodo, timeout_sec=0.05)
                while guion_ and guion_[0][0] <= time.time() - t0:
                    tecla = guion_.pop(0)[1]
                    print(f"[auto] tecla {tecla!r}", flush=True)
                    tecla_a_accion(tecla)
                for tecla in term.get_keys():
                    if not tecla_a_accion(tecla):
                        rclpy.shutdown()
                        return
    t = threading.Thread(target=correr, daemon=True, name="teleop")
    t.start()
    return t


def lanzar(caso="rayuela", *, visor=True, vision=True, control=True, ver_vision=False,
           objetivo=None, puntos=None, velocidad_patada=None, tabla_propia=None, editar_escena=None,
           monitor=False, altura_pato=None, editar_modelo=None, segundos=None, auto=None):
    """Arranca el caso de uso. Los ejercicios (exercises_rayuela/n4_*.py) llaman a esta funcion con SUS parametros.

    visor            abrir la ventana 3D del robot
    vision           ejecutar el nodo de VISION oficial (detecta donde cae la pelota)
    control          ejecutar el nodo de CONTROL oficial (el pato camina solo a la casilla donde cayo)
    ver_vision       ventana con lo que "ve" la camara, ya rectificado
    objetivo         casilla que hay que acertar (1-9), "aleatorio" o None (sin marcador)
    puntos           {0: aciertos, 1: casi (casilla vecina), 2: fallo} puntos de cada resultado
    velocidad_patada m/s fijos para las teclas k / l (None = las teclas piden la velocidad al cerebro por defecto)
    segundos, auto   solo para pruebas automaticas
    """
    if caso != "rayuela":
        raise SystemExit(f"El caso '{caso}' aun no esta listo.")
    print(__doc__)
    rclpy.init()
    rclpy._params.update({"vis_rect": ver_vision, "vis_raw": False})
    teleop_keyboard.TerminalInput = TecladoWindows

    if editar_escena:       # el cargador oficial abre el XML con MjSpec: aqui se le deja editar la escena antes de compilar
        _from_file = mujoco.MjSpec.from_file

        def _from_file_editado(*a, **k):
            spec = _from_file(*a, **k)
            editar_escena(spec)
            return spec
        mujoco.MjSpec.from_file = staticmethod(_from_file_editado)
    mundo = Mundo(sim_worker.XML_PATH, sim_worker.POLICIES_DIR, visor, segundos=segundos)
    if editar_escena:
        mujoco.MjSpec.from_file = staticmethod(_from_file)
    if editar_modelo:                    # ajustes sobre el mundo ya creado (p. ej. inclinar el balancin al empezar)
        editar_modelo(mundo.model, mundo.data)
        mujoco.mj_forward(mundo.model, mundo.data)
        mundo._snap = (mundo.data.qpos.copy(), mundo.data.qvel.copy())
    if altura_pato is not None:          # p. ej. el pato empieza SOBRE una plataforma: se sube su altura inicial
        mundo.data.qpos[mundo._qpos_adr + 2] = altura_pato
        mujoco.mj_forward(mundo.model, mundo.data)
        mundo._snap = (mundo.data.qpos.copy(), mundo.data.qvel.copy())
    TecladoWindows.mundo = mundo
    mundo.puente = Puente(mundo)
    hilo_nodo(lambda: mundo.puente, "puente")
    marcador = None
    if objetivo is not None:
        marcador = Marcador(objetivo, puntos or {0: 10, 1: 3, 2: 0})
        hilo_nodo(lambda: marcador, "marcador")
    if monitor:
        mon = Monitor()
        hilo_nodo(lambda: mon, "monitor")
    if vision:
        hilo_nodo(clase_nodo(vision_node), "vision")
    if control:
        hilo_nodo(clase_nodo(control_node), "control")
    tabla = None
    if tabla_propia:                       # json de n3_05: {"1": {"pie": ..., "velocidad": ...}, ...}
        import json
        ruta = pathlib.Path(tabla_propia)
        if ruta.exists():
            tabla = json.loads(ruta.read_text(encoding="utf-8"))
            print(f"Usando TU politica de patada: {ruta.name}")
        else:
            print(f"AVISO: no existe {ruta.name}: ejecuta antes n3_05_entrena_la_patada.py. Se usa la tabla oficial.")
    hilo_teleop(auto, velocidad_patada, marcador, tabla)
    try:
        mundo.run()
    finally:
        rclpy.shutdown()
    sys.stdout.flush()
    os._exit(0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("caso", choices=["rayuela", "patines", "cuerda"])
    ap.add_argument("--sin-visor", action="store_true")
    ap.add_argument("--sin-vision", action="store_true", help="no ejecuta vision_node")
    ap.add_argument("--sin-control", action="store_true", help="no ejecuta control_node")
    ap.add_argument("--ver-vision", action="store_true")
    ap.add_argument("--objetivo", default=None, help="casilla 1-9 o 'aleatorio': activa el marcador")
    ap.add_argument("--velocidad-patada", type=float, default=None)
    ap.add_argument("--segundos", type=float, default=None)
    ap.add_argument("--auto", default=None, help="prueba automatica: 'seg:tecla,seg:tecla'")
    a = ap.parse_args()
    guion = [(float(t), k) for t, k in (p.split(":") for p in a.auto.split(","))] if a.auto else None
    lanzar(a.caso, visor=not a.sin_visor, vision=not a.sin_vision, control=not a.sin_control,
           ver_vision=a.ver_vision, objetivo=a.objetivo, velocidad_patada=a.velocidad_patada,
           segundos=a.segundos, auto=guion)


if __name__ == "__main__":
    main()
