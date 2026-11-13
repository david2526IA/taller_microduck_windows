"""ENTORNO DE PRUEBA de la VOLTERETA (sin ventana): mide que hace cada checkpoint de la politica.

Mismo simulador que la Rayuela (MuJoCo + motores BAM + cerebros oficiales). Aqui se sustituye el cerebro de la voltereta
por el checkpoint que se quiera probar, se deja al pato de pie un segundo, se le ordena la voltereta y se miden tres cosas:

   giro      cuantos grados ha rotado el tronco hacia delante (una voltereta completa = 360)
   de pie    si, pasados unos segundos, acaba de pie
   altura    la altura final del tronco (de pie ~ 0,115 m; tumbado ~ 0,05 m)
"""
import contextlib, io, pathlib, sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import patada_env  # noqa: E402  (prepara las rutas y el simulador oficial)
import mujoco  # noqa: E402
import onnxruntime as ort  # noqa: E402
from rayuela import sim_setup  # noqa: E402

DURACION_VOLTERETA = 2.0       # s que dura la voltereta antes de devolver el control (igual que la Rayuela oficial)


def _angulo_pitch(quat):
    """Angulo (rad) del eje vertical del tronco en el plano x-z: 0 = de pie, +-pi = boca abajo."""
    m = np.zeros(9)
    mujoco.mju_quat2Mat(m, np.asarray(quat, dtype=float))
    m = m.reshape(3, 3)
    z = m[:, 2]                                   # eje "arriba" del tronco, en coordenadas del mundo
    return float(np.arctan2(z[0], z[2]))


class VolteretaEnv(patada_env.PatadaEnv):
    def reset(self):
        """Reinicio COMPLETO: sin esto el estado interno del simulador (tiempo, arranque en caliente del solver, ultima accion)
        pasa de un intento al siguiente y la MISMA prueba da resultados distintos. Para medir hay que partir siempre de cero."""
        w = self.w
        mujoco.mj_resetData(w.model, w.data)
        w.policy.last_action[:] = 0
        super().reset()

    def probar(self, onnx_path, segundos_asentar=1.0, segundos_tras=3.0):
        """Ejecuta UNA voltereta con el checkpoint 'onnx_path'. Devuelve (giro_grados, de_pie, altura_final, se_cayo_antes)."""
        w = self.w
        sesion = ort.InferenceSession(str(onnx_path))
        w.policy.behavior_sessions["roulade"] = sesion
        w.policy.behavior_durations["roulade"] = DURACION_VOLTERETA
        self.reset()
        a0 = self.w._qpos_adr
        with contextlib.redirect_stdout(io.StringIO()):
            for _ in range(int(segundos_asentar / w.control_dt)):
                sim_setup.step_behavior_timers(w.policy, w.control_dt)
                w.policy.apply_action(w.policy.infer())
                for _ in range(sim_setup.CONTROL_DECIMATION):
                    w.bam_ctrl.update()
                    mujoco.mj_step(w.model, w.data)
            w.policy.trigger_behavior("roulade")
            previo = _angulo_pitch(w.data.qpos[a0 + 3:a0 + 7])
            acumulado = 0.0
            for _ in range(int((DURACION_VOLTERETA + segundos_tras) / w.control_dt)):
                sim_setup.step_behavior_timers(w.policy, w.control_dt)
                w.policy.apply_action(w.policy.infer())
                for _ in range(sim_setup.CONTROL_DECIMATION):
                    w.bam_ctrl.update()
                    mujoco.mj_step(w.model, w.data)
                ang = _angulo_pitch(w.data.qpos[a0 + 3:a0 + 7])
                d = (ang - previo + np.pi) % (2 * np.pi) - np.pi          # diferencia sin saltos de +-pi
                acumulado += d
                previo = ang
        quat = w.data.qpos[a0 + 3:a0 + 7]
        m = np.zeros(9); mujoco.mju_quat2Mat(m, np.asarray(quat, dtype=float))
        vertical = float(m.reshape(3, 3)[2, 2])                          # 1 = de pie, -1 = boca abajo
        altura = float(w.data.qpos[a0 + 2])
        return abs(float(np.degrees(acumulado))), bool(vertical > 0.9 and altura > 0.09), altura
