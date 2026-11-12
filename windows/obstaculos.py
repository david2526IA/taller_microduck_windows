"""EL CIRCUITO DE OBSTACULOS (inspirado en la demo de NVIDIA del GTC Berlin 2026) en MuJoCo y en CPU.

En la demo de NVIDIA un agente de IA monta un circuito (plataformas, rampas, obstaculos) en Isaac Sim, se afina una politica
de andar en Isaac Lab con 4.096 robots en una GPU, y se VALIDA midiendo: obstaculos superados, caidas y colisiones.
Aqui se hace la parte que cabe en un PC sin GPU:
  - el circuito se DESCRIBE con codigo (crear_circuito) y se monta en MuJoCo: rampas, escalones, cuadricula irregular y escombros,
    las mismas familias de terreno que el entrenamiento de NVIDIA / Pollen (Isaac Lab: IsaacContrib-Velocity-Rough-MicroDuck);
  - se usan politicas YA ENTRENADAS (alpha_walking, y rough_walk_e / rough_walk_g de Hugging Face, entrenadas en terreno irregular);
  - se VALIDAN con las mismas metricas: circuito completado, caidas y donde se caen (evaluar).
Lo que NO se replica: el agente que construye el circuito, la camara de profundidad, Isaac Sim/Newton y el entrenamiento en GPU.
"""
import importlib.util, math, os, pathlib, sys, types

AQUI = pathlib.Path(__file__).resolve().parent.parent
OFICIAL = AQUI / "rayuela-oficial"
POLITICAS = AQUI / "windows" / "politicas"
CEREBROS = {
    "alpha_walking": OFICIAL / "policies-v1" / "alpha_walking.onnx",
    "rough_walk_e": POLITICAS / "rough_walk_e.onnx",
    "rough_walk_g": POLITICAS / "rough_walk_g.onnx",
}
ESCENA = OFICIAL / "src" / "mjlab_microduck" / "robot" / "microduck" / "scene.xml"

# Parametros por defecto del circuito (en metros y grados). Los ejercicios los cambian.
CIRCUITO = dict(
    ancho=1.0,                    # ancho del circuito (m)
    angulo_rampa=6.0,             # grados (NVIDIA: pendientes del 3 al 10 %  ~ 2 a 6 grados; aqui hasta 9 como en la bateria de Pollen)
    n_escalones=3, altura_escalon=0.010, ancho_escalon=0.15,        # NVIDIA: 0 a 1,5 cm, escalon de 15 cm
    altura_cuadricula=0.010, ancho_baldosa=0.15,                    # NVIDIA: cuadricula de 0 a 1 cm
    altura_escombros=0.015,                                          # +-0,2 a 2,5 cm en la bateria de Pollen
    semilla=0,
    nivel=4,                      # 0 a 4: cuantas cosas se activan (ver NIVELES)
)
X_INICIO, X_FIN = 0.5, 4.9        # donde empieza el primer obstaculo y la meta (m)
SECCIONES = [("rampa", 0.5, 1.3), ("escalones", 1.5, 2.5), ("cuadricula", 2.7, 3.5), ("escombros", 3.7, 4.5)]
# EL CRESCENDO: cada nivel anade UNA cosa. El circuito mide siempre lo mismo (misma meta); lo que no esta activo es suelo llano.
NIVELES = [
    "0 · llano (la referencia)", "1 · + rampa", "2 · + escalones", "3 · + cuadricula irregular",
    "4 · + escombros",
]


def rumbo_wz(data, cuerpo, k=1.5, tope=0.6):
    """Orden de giro que devuelve el pato a mirar hacia +x: proporcional al error de rumbo. Sin ella cada cerebro se desvia a su manera."""
    yaw = math.atan2(data.xmat[cuerpo][3], data.xmat[cuerpo][0])
    return max(-tope, min(tope, -k * yaw))


def seccion_en(x):
    """Nombre de la seccion del circuito en la que esta una posicion x (o 'llano')."""
    for nombre, a, b in SECCIONES:
        if a - 0.05 <= x <= b + 0.05:
            return nombre
    return "meta" if x >= X_FIN - 0.3 else "llano"


def crear_circuito(spec, **cfg):
    """DESCRIBE el circuito: aqui esta toda la 'escena'. Cada bloque anade piezas (cajas) al mundo de MuJoCo antes de crearlo."""
    import mujoco, random
    c = {**CIRCUITO, **cfg}
    rng = random.Random(c["semilla"])
    W = c["ancho"]
    gris = [0.55, 0.58, 0.62, 1]
    caja = lambda nombre, pos, tam, rgba=gris, euler=(0, 0, 0): spec.worldbody.add_geom(
        name=nombre, type=mujoco.mjtGeom.mjGEOM_BOX, pos=list(pos), size=list(tam), rgba=rgba, euler=list(euler),
        friction=[1.0, 0.005, 0.0001])

    nivel = int(c["nivel"])
    # --- RAMPA: sube, meseta, baja (como la "piramide de pendiente" del entrenamiento) ---
    th = math.radians(c["angulo_rampa"]) if nivel >= 1 else 0.0
    a, b = SECCIONES[0][1], SECCIONES[0][2]
    L = 0.3                                          # largo en x de cada rampa
    rise = L * math.tan(th)
    t = 0.02                                          # grosor de la chapa
    for i, (x0, signo) in enumerate(((a, +1), (b - L, -1)) if nivel >= 1 else ()):
        xm, h = x0 + L / 2, rise / 2
        n = (-signo * math.sin(th), 0.0, math.cos(th))   # normal de la superficie
        centro = (xm, 0.0, h - n[2] * t / 2 if signo > 0 else h - n[2] * t / 2)
        caja(f"rampa_{i}", (centro[0] - n[0] * t / 2, 0, h - n[2] * t / 2), (L / (2 * math.cos(th)), W / 2, t / 2),
             euler=(0, -signo * th, 0))
    if nivel >= 1:
        caja("rampa_meseta", ((a + L + b - L) / 2, 0, rise / 2), ((b - L - a - L) / 2, W / 2, rise / 2))
    # --- ESCALONES: suben, meseta, bajan ---
    s0, s1 = SECCIONES[1][1], SECCIONES[1][2]
    n_e, h_e, w_e = (int(c["n_escalones"]) if nivel >= 2 else 0), c["altura_escalon"], c["ancho_escalon"]
    n_e = min(n_e, int((s1 - s0) / (2 * w_e)))        # que quepan los escalones de subida y de bajada
    for i in range(n_e):
        for lado, x in (("s", s0 + i * w_e + w_e / 2), ("b", s1 - i * w_e - w_e / 2)):
            alto = (i + 1) * h_e
            caja(f"escalon_{lado}{i}", (x, 0, alto / 2), (w_e / 2, W / 2, alto / 2), rgba=[0.62, 0.55, 0.45, 1])
    if n_e:
        alto = n_e * h_e
        caja("escalon_meseta", ((s0 + n_e * w_e + s1 - n_e * w_e) / 2, 0, alto / 2),
             (((s1 - s0) - 2 * n_e * w_e) / 2, W / 2, alto / 2), rgba=[0.62, 0.55, 0.45, 1])
    # --- CUADRICULA IRREGULAR: baldosas con altura al azar ---
    g0, g1 = SECCIONES[2][1], SECCIONES[2][2]
    bw, hg = c["ancho_baldosa"], c["altura_cuadricula"]
    nx, ny = (int((g1 - g0) / bw), int(W / bw)) if nivel >= 3 else (0, 0)
    for i in range(nx):
        for j in range(ny):
            alto = max(0.001, rng.uniform(0, hg))
            caja(f"baldosa_{i}_{j}", (g0 + (i + 0.5) * bw, -W / 2 + (j + 0.5) * bw, alto / 2), (bw / 2, bw / 2, alto / 2),
                 rgba=[0.5 + 0.4 * alto / max(hg, 1e-3), 0.55, 0.6, 1])
    # --- ESCOMBROS: bultos pequenos de tamano y altura al azar ---
    e0, e1 = SECCIONES[3][1], SECCIONES[3][2]
    for k in range(int(40 * W) if nivel >= 4 else 0):
        sx, sy = rng.uniform(0.03, 0.07), rng.uniform(0.03, 0.07)
        alto = rng.uniform(0.002, max(0.003, c["altura_escombros"]))
        caja(f"escombro_{k}", (rng.uniform(e0, e1), rng.uniform(-W / 2 + 0.05, W / 2 - 0.05), alto / 2), (sx, sy, alto / 2),
             rgba=[0.7, 0.45, 0.3, 1], euler=(0, 0, rng.uniform(0, math.pi)))
    # --- META: una franja roja ---
    spec.worldbody.add_geom(name="meta", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[X_FIN, 0, 0.0015], size=[0.03, W / 2, 0.0015],
                            rgba=[0.9, 0.15, 0.15, 1], contype=0, conaffinity=0)
    return spec


def _cargar_oficial():
    for _n in ("termios", "tty"):
        sys.modules.setdefault(_n, types.ModuleType(_n))
    sys.modules["tty"].setcbreak = lambda *a, **k: None
    os.environ["MICRODUCK_RL_ROOT"] = str(OFICIAL)
    os.chdir(OFICIAL)
    sys.path.insert(0, str(OFICIAL / "scripts"))
    sp = importlib.util.spec_from_file_location("infer_policy", OFICIAL / "scripts" / "infer_policy.py")
    ip = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(ip)
    return ip


def evaluar(cerebro, pruebas=10, avance=0.4, segundos_max=90.0, semilla=0, cfg=None, verbose=False, mantener_rumbo=True):
    """VALIDA una politica en el circuito, como la parte de validacion de NVIDIA: lanza 'pruebas' recorridos
    (con un pequeño azar al empezar) y cuenta cuantos completan el circuito, cuantas caidas hay y donde.
    Devuelve un dict con: completados, caidas, atascados, distancia media (m) y caidas por seccion."""
    import contextlib, io
    import mujoco, numpy as np
    ip = _cargar_oficial()
    ruta = pathlib.Path(cerebro) if os.path.exists(str(cerebro)) else CEREBROS[cerebro]
    _from_file = mujoco.MjSpec.from_file

    def con_circuito(*a, **k):
        return crear_circuito(_from_file(*a, **k), **(cfg or {}))
    mujoco.MjSpec.from_file = staticmethod(con_circuito)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            bam = ip.load_bam_model(ip.BAM_KP_FW, 7.4, 0.0)
            model, data, bam_ctrl, _ = ip.load_mujoco_with_bam(str(ESCENA), bam, 0.005, 0.1, ip.BAM_VIN_MIN)
    finally:
        mujoco.MjSpec.from_file = staticmethod(_from_file)
    rng = np.random.default_rng(semilla)
    adr = model.jnt_qposadr[model.joint("trunk_base_freejoint").id]
    cuerpo = model.body("trunk_base").id
    res = dict(completados=0, caidas=0, atascados=0, distancias=[], caidas_en={}, finales=[])
    for k in range(pruebas):
        mujoco.mj_resetData(model, data)
        with contextlib.redirect_stdout(io.StringIO()):
            pol = ip.PolicyInference(model, data, bam_ctrl=bam_ctrl, walking_onnx_path=str(ruta),
                                     standing_onnx_path=str(CEREBROS["alpha_walking"]).replace("walking", "standing"),
                                     action_scale=1.0, delay_min_lag=0, delay_max_lag=0, switch_threshold=0.1,
                                     use_projected_gravity=True, new_cmd_obs=True)
            data.qpos[adr:adr + 3] = [0.0, rng.uniform(-0.1, 0.1), 0.125]
            yaw = rng.uniform(-0.09, 0.09)
            data.qpos[adr + 3:adr + 7] = [math.cos(yaw / 2), 0, 0, math.sin(yaw / 2)]
            for i, q in enumerate(pol.joint_qpos_indices):
                data.qpos[q] = pol.default_pose[i]
            bam_ctrl.reset(data.qpos)
            pol.set_position_targets(pol.default_pose)
            mujoco.mj_forward(model, data)
            pol.set_vel_cmd(avance, 0.0, 0.0)
            pasos, x_max, fin = int(segundos_max / 0.02), 0.0, "atascado"
            for _paso in range(pasos):
                if mantener_rumbo and _paso % 5 == 0:                 # corrige el rumbo (como la orden de "heading" de NVIDIA)
                    pol.set_vel_cmd(avance, 0.0, rumbo_wz(data, cuerpo))
                pol.apply_action(pol.infer())
                for _ in range(4):
                    bam_ctrl.update()
                    mujoco.mj_step(model, data)
                x = float(data.xpos[cuerpo][0])
                x_max = max(x_max, x)
                tilt = math.degrees(math.acos(max(-1.0, min(1.0, data.xmat[cuerpo][8]))))
                if tilt > 55 or data.xpos[cuerpo][2] < 0.05:
                    fin = "caida"
                    break
                if x >= X_FIN:
                    fin = "completado"
                    break
        res["distancias"].append(x_max)
        res["finales"].append((round(float(data.xpos[cuerpo][1]), 2), round(math.degrees(math.atan2(data.xmat[cuerpo][3], data.xmat[cuerpo][0])), 0)))
        if fin == "completado":
            res["completados"] += 1
        elif fin == "caida":
            res["caidas"] += 1
            sec = seccion_en(x_max)
            res["caidas_en"][sec] = res["caidas_en"].get(sec, 0) + 1
        else:
            res["atascados"] += 1
        if verbose:
            print(f"  prueba {k + 1}/{pruebas}: {fin} (llego a x={x_max:.2f} m)", flush=True)
    res["distancia_media"] = float(np.mean(res["distancias"]))
    return res
