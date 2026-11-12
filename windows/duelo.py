"""EL DUELO DE LA CUERDA con la politica ENTRENADA (patos_cuerda / duelo2), en MuJoCo normal y en CPU.

Dos Microducks atados por una cuerda, cada uno mirando hacia fuera (A en x=-0.5, B en x=+0.5). Gana quien consigue que
el otro cruce SU linea de color: A gana si B llega a x <= -0.35 (linea azul); B gana si A llega a x >= +0.35 (linea roja).
Pierde tambien el que se cae. Un solo cerebro juega los dos lados (autojuego): el mismo .onnx para A y para B.

Como se hizo (para contarlo en el taller): el cerebro se entreno con mjlab + PPO en una GPU (proyecto patos_cuerda, rama
tug-etapas de microduck_rl): 6000+ iteraciones de autojuego con una recompensa competitiva (ganar, tirar de la cuerda tensa,
no caerse...). Aqui solo se EJECUTA (inferencia), con los motores BAM y la fisica de MuJoCo, sin torch ni GPU.
"""
import os, pathlib, queue, sys, threading, time, types
import msvcrt

for _f in (sys.stdout, sys.stderr):
    _f.reconfigure(encoding="utf-8", errors="replace")

AQUI = pathlib.Path(__file__).resolve().parent.parent
OFICIAL = AQUI / "rayuela-oficial"
ESCENA = AQUI / "windows" / "escenas" / "dos_patos.xml"
POLITICA_DUELO = AQUI / "windows" / "politicas" / "duelo2.onnx"
for _n in ("termios", "tty"):
    sys.modules.setdefault(_n, types.ModuleType(_n))
sys.path.insert(0, str(OFICIAL / "scripts"))

import mujoco  # noqa: E402
import mujoco.viewer  # noqa: E402
import numpy as np  # noqa: E402
import onnxruntime as ort  # noqa: E402
import multi_duck_controller as mdc  # noqa: E402  (oficial: la clase Duck con la observacion de 61 numeros)
import cuerda  # noqa: E402  (genera la escena de dos patos)

LINEA = 0.35                      # linea de victoria (m)
HOME = [(-0.5, (0, 0, 0, 1)), (0.5, (1, 0, 0, 0))]       # A y B, cada uno mirando hacia fuera


class Teclado:
    def __init__(self):
        self.cola = queue.Queue()
        threading.Thread(target=self._leer, daemon=True).start()

    def _leer(self):
        while True:
            if not msvcrt.kbhit():
                time.sleep(0.02)
                continue
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue
            self.cola.put(ch.lower())


def cargar_mundo(largo_cuerda, masa_a, masa_b, rozamiento, separacion):
    """Escena oficial de dos patos + la cuerda (un tendon) y motores BAM, igual que en el entrenamiento."""
    import importlib.util
    cuerda._generar_escena()
    spec_ip = importlib.util.spec_from_file_location("infer_policy", OFICIAL / "scripts" / "infer_policy.py")
    ip = importlib.util.module_from_spec(spec_ip)
    spec_ip.loader.exec_module(ip)
    _from_file = mujoco.MjSpec.from_file

    def con_cuerda(*a, **k):
        spec = _from_file(*a, **k)
        for i in (0, 1):
            b = next(b for b in spec.bodies if b.name == f"duck{i}_trunk_base")
            b.add_site(name=f"cuerda_{i}", pos=[-0.05, 0, 0], size=[0.012] * 3, rgba=[1, 0, 0, 1])
        t = spec.add_tendon(name="tug_rope", limited=True, range=[0.0, largo_cuerda], width=0.006, rgba=[0.9, 0.7, 0.2, 0.0])
        t.wrap_site("cuerda_0"); t.wrap_site("cuerda_1")
        for g in spec.geoms:
            if g.name == "floor":
                g.friction[0] = rozamiento
        for i, esc in ((0, masa_a), (1, masa_b)):
            if esc != 1.0:
                next(b for b in spec.bodies if b.name == f"duck{i}_trunk_base").mass *= esc
        return spec
    mujoco.MjSpec.from_file = staticmethod(con_cuerda)
    try:
        bam = ip.load_bam_model(ip.BAM_KP_FW, 7.4, 0.0)
        model, data, bam_ctrl, nombres = ip.load_mujoco_with_bam(str(ESCENA), bam, 0.005, 0.1, ip.BAM_VIN_MIN)
    finally:
        mujoco.MjSpec.from_file = staticmethod(_from_file)
    return model, data, bam_ctrl, nombres


def lanzar_duelo(avance_a=0.6, avance_b=0.6, tiempo_max=20.0, fuerza_b=1.0, masa_a=1.0, masa_b=1.0, rozamiento=1.0, largo_cuerda=1.0, desplazamiento=0.0,
                 politica_a=None, politica_b=None, b_solo_anda=False, ruido_inicial=0.03, semilla=None, visor=True, segundos=None, combates=None, verbose=True):
    """
    avance_a/_b     la orden de AVANCE que recibe cada cerebro (0 a 1 m/s): cuanto "quiere" tirar. Con 0 se queda de pie sin tirar.
    tiempo_max      segundos de combate; si nadie gana, empate (como en el entrenamiento: 20 s).
    fuerza_b        escala de las ordenes del pato B (1.0 = igual de fuerte; 0.7 = un 30 % mas flojo). El curriculo de fuerza del entrenamiento.
    masa_a/masa_b   masa del tronco de cada pato (1.0 = normal).
    rozamiento      agarre de los pies (1.0 normal, 0.3 hielo).
    largo_cuerda    longitud maxima de la cuerda en metros (los patos empiezan a 0.9 m).
    desplazamiento  cuanto se acerca cada pato al centro al empezar (m): 0 = como en el entrenamiento; 0.1 = mas cerca (empieza ya tenso).
    ruido_inicial   variacion al azar de la posicion y el giro al empezar (m). 0 = el mismo combate siempre (y gana siempre el mismo: el duelo es simetrico).
    politica_a/_b   cerebro .onnx de cada pato (por defecto el entrenado en el duelo).
    b_solo_anda     True: B usa el cerebro de ANDAR (no entrenado para el duelo) pidiendole avanzar. ¿Cuanto aporta entrenar con una recompensa competitiva?
    """
    model, data, bam_ctrl, nombres = cargar_mundo(largo_cuerda, masa_a, masa_b, rozamiento, 1.0)
    ducks = [mdc.Duck(model, i, True) for i in (0, 1)]
    if b_solo_anda:
        politica_b = politica_b or OFICIAL / "policies-v1" / "alpha_walking.onnx"
    ses = [ort.InferenceSession(str(politica_a or POLITICA_DUELO)), ort.InferenceSession(str(politica_b or POLITICA_DUELO))]
    fuerza = [1.0, fuerza_b]
    avance = [avance_a, avance_b]
    marcador = {"A": 0, "B": 0, "empates": 0, "caidas": 0}
    rng = np.random.default_rng(semilla)

    def inicio():
        """Pone a los dos patos en su sitio, mirando hacia FUERA, con un pequeño azar para que cada combate sea distinto."""
        mujoco.mj_resetData(model, data)
        for i, (d, (x, q)) in enumerate(zip(ducks, HOME)):
            xi = x - np.sign(x) * desplazamiento + rng.uniform(-ruido_inicial, ruido_inicial)
            yi = rng.uniform(-ruido_inicial, ruido_inicial)
            d.set_initial_pose(data, xi, yi)
            giro = rng.uniform(-0.1, 0.1) if ruido_inicial else 0.0              # +-6 grados
            yaw0 = 0.0 if i == 1 else np.pi
            data.qpos[d.qpos_adr + 3:d.qpos_adr + 7] = [np.cos((yaw0 + giro) / 2), 0, 0, np.sin((yaw0 + giro) / 2)]
            d.last_action[:] = 0
            d.vel_cmd[:] = 0
        mujoco.mj_forward(model, data)
        bam_ctrl.reset(data.qpos)
    inicio()

    n_a = len(ducks[0].actuator_ids)
    q_obj = np.zeros(len(nombres))
    kb = Teclado() if sys.stdin.isatty() else None
    sa, sb = model.site("cuerda_0").id, model.site("cuerda_1").id
    visor_ctx = mujoco.viewer.launch_passive(model, data) if visor else None
    print(__doc__)
    print("TECLAS: n = nuevo combate | w / s = A tira mas / menos | i / k = B tira mas / menos | q = salir")
    print("        Ctrl + clic derecho sobre un pato = empujarlo")
    t0, paso, t_combate, ultimo = time.time(), 0, 0.0, 0.0
    fin_combate = None
    try:
        while (visor_ctx is None or visor_ctx.is_running()) and not (segundos and time.time() - t0 > segundos):
            t_paso = time.time()
            if paso % mdc.DECIMATION == 0:
                for i, d in enumerate(ducks):
                    d.vel_cmd[:] = [avance[i], 0.0, 0.0]      # "avanza": cada pato, hacia el lado al que mira (hacia fuera)
                    obs = d.get_observation(model, data)
                    a = ses[i].run(None, {ses[i].get_inputs()[0].name: obs[None, :]})[0][0].astype(np.float32)
                    d.last_action = a.copy()
                    obj = d.default_pose + a * fuerza[i]
                    q_obj[i * n_a:(i + 1) * n_a] = obj
                bam_ctrl.q_target[:] = q_obj
            bam_ctrl.update()
            mujoco.mj_step(model, data)
            paso += 1
            if visor_ctx:
                g = visor_ctx.user_scn.geoms[0]
                mujoco.mjv_connector(g, mujoco.mjtGeom.mjGEOM_CAPSULE, 0.008, data.site_xpos[sa], data.site_xpos[sb])
                g.rgba[:] = [0.9, 0.7, 0.2, 1]
                visor_ctx.user_scn.ngeom = 1
                visor_ctx.sync()
            xa = float(data.xpos[ducks[0].trunk_base_id][0]); xb = float(data.xpos[ducks[1].trunk_base_id][0])
            za = float(data.xpos[ducks[0].trunk_base_id][2]); zb = float(data.xpos[ducks[1].trunk_base_id][2])
            resultado, cae = None, None
            if xb <= -LINEA:
                resultado = "A"
            elif xa >= LINEA:
                resultado = "B"
            elif data.time > tiempo_max:
                resultado = "empate"
            elif za < 0.07 and zb < 0.07:
                resultado = "empate"
            elif za < 0.07:
                resultado = "B"; cae = "A"
            elif zb < 0.07:
                resultado = "A"; cae = "B"
            if resultado and fin_combate is None:
                fin_combate = time.time()
                marcador["empates" if resultado == "empate" else resultado] += 1
                marcador["caidas"] += 1 if cae else 0
                print(f"\n=== COMBATE: gana {resultado}  (A {marcador['A']} - B {marcador['B']}, empates {marcador['empates']}) ===\n", flush=True)
            if fin_combate and time.time() - fin_combate > 1.5:
                inicio(); paso = 0; fin_combate = None
                if combates and sum(marcador[k] for k in ("A", "B", "empates")) >= combates:
                    break
            while kb and not kb.cola.empty():
                c = kb.cola.get()
                if c == "n":
                    inicio(); paso = 0; fin_combate = None; print("\n>> NUEVO COMBATE\n", flush=True)
                elif c in "wsik":
                    j = 0 if c in "ws" else 1
                    avance[j] = float(np.clip(avance[j] + (0.1 if c in "wi" else -0.1), 0.0, 1.0))
                    print(f">> orden de avance (cuanto tira): A={avance[0]:.1f}  B={avance[1]:.1f}", flush=True)
                elif c == "q":
                    return marcador
            if verbose and time.time() - ultimo > 1.0:
                ultimo = time.time()
                print(f"[duelo] t={data.time:4.1f}s  A x={xa:+.2f} (alto {za*1000:3.0f} mm)   B x={xb:+.2f} (alto {zb*1000:3.0f} mm)   "
                      f"lineas: A gana si B<={-LINEA:+.2f}, B gana si A>={LINEA:+.2f}", flush=True)
            espera = mdc.TIMESTEP - (time.time() - t_paso)
            if espera > 0 and visor_ctx:
                time.sleep(espera)
    finally:
        if visor_ctx:
            visor_ctx.close()
    return marcador


if __name__ == "__main__":
    print(lanzar_duelo(visor=False, segundos=60, combates=3))
