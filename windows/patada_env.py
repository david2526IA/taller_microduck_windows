"""ENTORNO DE ENTRENAMIENTO de la patada (sin ventana, lo mas rapido que da la CPU).

En RL un "entorno" es algo con dos metodos: reset() lo deja todo en el punto de partida y step(accion) ejecuta una
accion y devuelve lo que paso. Aqui la accion es "a que velocidad (m/s) pateo la pelota" y el resultado es
"donde se paro la pelota". Por dentro corre la MISMA simulacion que la Rayuela: MuJoCo + motores BAM + el cerebro
ONNX de patada del repo oficial. Lo que se entrena en n3_05 es QUE VELOCIDAD ELEGIR; el cerebro de patada ya viene hecho.
"""
import os, pathlib, sys, types

for _f in (sys.stdout, sys.stderr):             # la consola de Windows no sabe escribir la flecha del codigo oficial
    _f.reconfigure(encoding="utf-8", errors="replace")

AQUI = pathlib.Path(__file__).resolve().parent.parent
OFICIAL = AQUI / "rayuela-oficial"
for _n in ("termios", "tty"):
    sys.modules.setdefault(_n, types.ModuleType(_n))
sys.modules["tty"].setcbreak = lambda *a, **k: None
os.environ["MICRODUCK_RL_ROOT"] = str(OFICIAL)
os.chdir(OFICIAL)
sys.path.insert(0, str(OFICIAL / "scripts"))
sys.path.insert(0, str(OFICIAL / "ros2_microduck" / "src" / "rayuela"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "ros_shim"))

import mujoco  # noqa: E402
import numpy as np  # noqa: E402

from rayuela import board_geometry, sim_setup, sim_worker  # noqa: E402  (codigo oficial)


class _SinCamara:                      # en entrenamiento no hace falta renderizar nada
    def __init__(self, model): pass
    def close(self): pass


sim_setup.SimCameras = _SinCamara


class PatadaEnv:
    def __init__(self, gravedad=9.81, masa_pelota=None, rozamiento_pelota=None, segundos_tras_patada=4.0, segundos_asentar=1.0):
        """
        gravedad            m/s^2 (9.81 = Tierra, 1.62 = Luna).  AFECTA A: cuanto tarda en pararse la pelota y a la patada.
        masa_pelota         kg (None = la del modelo).           AFECTA A: lo lejos que llega con la misma velocidad.
        rozamiento_pelota   rozamiento suelo-pelota (None = el del modelo). AFECTA A: cuanto rueda tras caer.
        segundos_tras_patada cuanto se espera a que la pelota se pare (4 s: a los 6 s de la patada ya esta a menos de 3 cm de donde acaba).
        segundos_asentar    el pato se queda de pie este tiempo ANTES de patear. Sin ello la patada sale mas corta y torcida
                            (medido: casilla 5 con 0 s -> x=1,18; con 1 s -> x=1,37, igual que en la partida de la Rayuela).
        """
        self.w = sim_worker.SimWorker(sim_worker.XML_PATH, sim_worker.POLICIES_DIR, False)
        m = self.w.model
        m.opt.gravity[2] = -abs(gravedad)
        self.ball_body = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
        self.ball_geom = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "ball_geom")
        self.base_masa = float(m.body_mass[self.ball_body])                      # los del modelo, para set_mundo(None)
        self.base_roz = m.geom_friction[self.ball_geom].copy()                   # (deslizamiento, giro, rodadura) de la pelota
        self.set_mundo(gravedad, masa_pelota, rozamiento_pelota)
        self.snap = (self.w.data.qpos.copy(), self.w.data.qvel.copy())
        self.espera = segundos_tras_patada
        self.asentar = segundos_asentar

    def set_mundo(self, gravedad=9.81, masa_pelota=None, rozamiento_pelota=None):
        """Cambia el mundo entre patada y patada (lo que hace la ALEATORIZACION DE DOMINIO: entrenar en mundos distintos).
        masa_pelota / rozamiento_pelota None = los del modelo."""
        m = self.w.model
        m.opt.gravity[2] = -abs(gravedad)
        m.body_mass[self.ball_body] = self.base_masa if masa_pelota is None else masa_pelota
        factor = 1.0 if rozamiento_pelota is None else rozamiento_pelota / self.base_roz[0]
        m.geom_friction[self.ball_geom] = self.base_roz * factor                 # rozamiento de la pelota (el del modelo es 0.5)

    def reset(self):
        import contextlib, io
        w = self.w
        with contextlib.redirect_stdout(io.StringIO()):          # stop_all() imprime un aviso en cada reinicio
            w.policy.stop_all()
        w.data.qpos[:], w.data.qvel[:] = self.snap
        w.data.ctrl[:] = 0
        w.bam_ctrl.reset(w.data.qpos)
        w.policy.set_position_targets(w.policy.default_pose)
        mujoco.mj_forward(w.model, w.data)

    def step(self, velocidad, pie="kick_right"):
        """Pateo a 'velocidad' m/s con 'pie'. Devuelve (x, y, casilla, se_cayo) de donde se paro la pelota."""
        import contextlib, io
        self.reset()
        w = self.w
        with contextlib.redirect_stdout(io.StringIO()):          # el codigo oficial imprime mucho
            for _ in range(int(self.asentar / w.control_dt)):     # de pie un rato antes de patear
                sim_setup.step_behavior_timers(w.policy, w.control_dt)
                w.policy.apply_action(w.policy.infer())
                for _ in range(sim_setup.CONTROL_DECIMATION):
                    w.bam_ctrl.update()
                    mujoco.mj_step(w.model, w.data)
            w.policy.trigger_behavior(pie, kick_speed=float(velocidad))
            total = sim_setup.KICK_DURATION_S + self.espera
            cayo = False
            for _ in range(int(total / w.control_dt)):
                sim_setup.step_behavior_timers(w.policy, w.control_dt)
                w.policy.apply_action(w.policy.infer())
                for _ in range(sim_setup.CONTROL_DECIMATION):
                    w.bam_ctrl.update()
                    mujoco.mj_step(w.model, w.data)
                cayo = cayo or bool(w.data.qpos[w._qpos_adr + 2] < 0.07)
        x, y = (float(v) for v in w.data.xpos[self.ball_body][:2])
        return x, y, board_geometry.casilla_for_point(x, y), cayo
