"""CASO CUERDA (tug of war): dos Microducks unidos por una cuerda, cada uno tirando hacia su lado.

Que es y que NO es (hay que decirlo claro en el taller):
  - SI: el entorno MuJoCo de dos robots y una cuerda (un "tendon" con longitud maxima), con el cerebro de ANDAR oficial
        manejando a cada pato. Cada pato "tira" pidiendole al cerebro que ande hacia delante (de espaldas a la cuerda).
  - NO: un cerebro entrenado para el tira y afloja. El repo microduck-tug-of-war es una base experimental SIN politica
        competitiva entrenada. Aqui se ve como se MONTA el entorno y lo que habria que entrenar (recompensa competitiva).

La escena se construye con scripts/build_multi_duck_scene.py y scripts/multi_duck_controller.py del repo oficial (sin tocarlos).
"""
import os, pathlib, sys, threading, time, queue, types
import msvcrt

for _f in (sys.stdout, sys.stderr):
    _f.reconfigure(encoding="utf-8", errors="replace")

AQUI = pathlib.Path(__file__).resolve().parent.parent
OFICIAL = AQUI / "rayuela-oficial"
ESCENA = AQUI / "windows" / "escenas" / "dos_patos.xml"
for _n in ("termios", "tty"):
    sys.modules.setdefault(_n, types.ModuleType(_n))
sys.path.insert(0, str(OFICIAL / "scripts"))

import mujoco  # noqa: E402
import mujoco.viewer  # noqa: E402
import numpy as np  # noqa: E402
import onnxruntime as ort  # noqa: E402
import multi_duck_controller as mdc  # noqa: E402  (codigo oficial: la clase Duck y las constantes)


def _generar_escena():
    """Crea windows/escenas/dos_patos.xml con el constructor oficial de escenas (una sola vez)."""
    import subprocess
    if ESCENA.exists():
        return
    ESCENA.parent.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(OFICIAL / "scripts" / "build_multi_duck_scene.py"),
                    "--scene", str(OFICIAL / "src/mjlab_microduck/robot/microduck/scene.xml"),
                    "--n", "2", "--layout", "line", "--spacing", "1.0", "--out", str(ESCENA)],
                   cwd=OFICIAL, check=True, capture_output=True)
    txt = ESCENA.read_text(encoding="utf-8")
    ESCENA.write_text(txt.replace('meshdir="assets"',
                                  f'meshdir="{(OFICIAL / "src/mjlab_microduck/robot/microduck/assets").as_posix()}"'),
                      encoding="utf-8")


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


def lanzar_cuerda(fuerza_a=0.15, fuerza_b=0.15, escala_masa_a=1.0, escala_masa_b=1.0, rozamiento_suelo=1.0,
                  largo_cuerda=1.0, rigidez_cuerda=0.0, visor=True, segundos=None, politica_andar=None, politica_quieto=None):
    """
    fuerza_a / fuerza_b   velocidad que pide cada pato al cerebro de andar (0 a 0.3 m/s): cuanto TIRA cada uno.
    escala_masa_a / _b    masa del tronco de cada pato (1.0 = normal). Un pato mas pesado es mas dificil de arrastrar.
    rozamiento_suelo      agarre de los pies al suelo (1.0 normal, 0.2 hielo).
    largo_cuerda          longitud maxima de la cuerda en metros (los patos empiezan a 0.9 m: con 1.0 hay 10 cm de holgura).
    rigidez_cuerda        0 = cuerda que no se estira; >0 = elastica (mas alto = mas dura).
    """
    _generar_escena()
    spec = mujoco.MjSpec.from_file(str(ESCENA))
    # --- la CUERDA: un sitio en la espalda de cada pato y un tendon entre los dos (lo mismo que hace el repo microduck-tug-of-war) ---
    for i in (0, 1):
        body = next(b for b in spec.bodies if b.name == f"duck{i}_trunk_base")
        body.add_site(name=f"cuerda_{i}", pos=[-0.05, 0, 0], size=[0.012] * 3, rgba=[1, 0, 0, 1])
    cuerda = spec.add_tendon(name="tug_rope", limited=True, range=[0.0, largo_cuerda], width=0.006, rgba=[0.9, 0.7, 0.2, 0.0])   # el tendon hace la fisica; el dibujo de la cuerda va aparte
    if rigidez_cuerda > 0:
        cuerda.stiffness = rigidez_cuerda
    cuerda.wrap_site("cuerda_0")
    cuerda.wrap_site("cuerda_1")
    for g in spec.geoms:
        if g.name == "floor":
            g.friction[0] = rozamiento_suelo
    for i, esc in ((0, escala_masa_a), (1, escala_masa_b)):
        if esc != 1.0:
            next(b for b in spec.bodies if b.name == f"duck{i}_trunk_base").mass *= esc
    model = spec.compile()
    model.opt.timestep = mdc.TIMESTEP
    data = mujoco.MjData(model)

    ducks = [mdc.Duck(model, i, True) for i in (0, 1)]
    mando = [fuerza_a, fuerza_b]
    inicio = [(-0.5, 0.0, (0, 0, 0, 1)), (0.5, 0.0, (1, 0, 0, 0))]       # (x, y, giro): cada pato mira hacia FUERA

    def poner_inicio():
        mujoco.mj_resetData(model, data)
        for d, (x, y, q) in zip(ducks, inicio):
            d.set_initial_pose(data, x, y)
            data.qpos[d.qpos_adr + 3:d.qpos_adr + 7] = q
        mujoco.mj_forward(model, data)
        for d in ducks:
            d.last_action[:] = 0
    poner_inicio()

    pol = pathlib.Path(politica_andar or OFICIAL / "policies-v1" / "alpha_walking.onnx")
    qui = pathlib.Path(politica_quieto or OFICIAL / "policies-v1" / "alpha_standing.onnx")
    sess_andar, sess_quieto = ort.InferenceSession(str(pol)), ort.InferenceSession(str(qui))
    kb = Teclado() if sys.stdin.isatty() else None
    print(__doc__)
    print("TECLAS: w/s = pato A (izquierda) tira mas/menos | i/k = pato B (derecha) tira mas/menos | espacio = soltar\n"
          "        n = REINICIAR | q = salir")

    def paso_control():
        for i, d in enumerate(ducks):
            d.vel_cmd[:] = [mando[i], 0.0, 0.0]
            s = sess_andar if mando[i] > 0.05 else sess_quieto
            obs = d.get_observation(model, data)
            a = s.run(None, {s.get_inputs()[0].name: obs[None, :]})[0][0]
            d.apply_action(data, a.astype(np.float32), 1.0)

    def pos_x(i):
        return float(data.xpos[ducks[i].trunk_base_id][0])

    s_a, s_b = model.site("cuerda_0").id, model.site("cuerda_1").id
    visor_ctx = mujoco.viewer.launch_passive(model, data) if visor else None
    t0, paso, ultimo = time.time(), 0, 0
    try:
        while (visor_ctx is None or visor_ctx.is_running()) and not (segundos and time.time() - t0 > segundos):
            t_paso = time.time()
            if paso % mdc.DECIMATION == 0:
                paso_control()
            mujoco.mj_step(model, data)
            if visor_ctx:
                # La cuerda se dibuja aparte, siempre recta entre los dos sitios (el dibujo del tendon en el visor sale torcido)
                g = visor_ctx.user_scn.geoms[0]
                mujoco.mjv_connector(g, mujoco.mjtGeom.mjGEOM_CAPSULE, 0.006, data.site_xpos[s_a], data.site_xpos[s_b])
                g.rgba[:] = [0.9, 0.7, 0.2, 1]
                visor_ctx.user_scn.ngeom = 1
                visor_ctx.sync()
            paso += 1
            while kb and not kb.cola.empty():
                c = kb.cola.get()
                if c == "w": mando[0] = min(0.3, mando[0] + 0.05)
                elif c == "s": mando[0] = max(0.0, mando[0] - 0.05)
                elif c == "i": mando[1] = min(0.3, mando[1] + 0.05)
                elif c == "k": mando[1] = max(0.0, mando[1] - 0.05)
                elif c == " ": mando[0] = mando[1] = 0.0
                elif c == "n": poner_inicio(); print("\n>> REINICIO: patos en su sitio\n", flush=True)
                elif c == "q": return
            if time.time() - ultimo > 1.0:
                ultimo = time.time()
                # progreso de cada pato = cuanto ha avanzado en la direccion hacia la que MIRA (lejos del centro)
                pa = -(pos_x(0) - inicio[0][0])
                pb = pos_x(1) - inicio[1][0]
                zs = [float(data.xpos[d.trunk_base_id][2]) * 1000 for d in ducks]
                dif = pa - pb
                quien = "EMPATE" if abs(dif) < 0.15 else ("A GANA TERRENO (arrastra a B)" if dif > 0 else "B GANA TERRENO (arrastra a A)")
                print(f"[tira] A={mando[0]:.2f} m/s  B={mando[1]:.2f} m/s | avance A={pa:+.2f} m  B={pb:+.2f} m | "
                      f"altura tronco A={zs[0]:.0f} mm B={zs[1]:.0f} mm | {quien}", flush=True)
            espera = mdc.TIMESTEP - (time.time() - t_paso)
            if espera > 0 and visor_ctx:
                time.sleep(espera)
    finally:
        if visor_ctx:
            visor_ctx.close()
        return model, data, ducks


if __name__ == "__main__":
    import mujoco.viewer  # noqa: F401
    lanzar_cuerda(segundos=20, visor=False)
