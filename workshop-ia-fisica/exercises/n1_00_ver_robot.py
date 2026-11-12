"""NIVEL 1 - Conoce a tu robot (sin codigo que tocar).
Abre el robot en el visor de MuJoCo. Prueba:
  - Raton izq: rotar | der: mover | rueda: zoom
  - Doble clic en el robot y  Ctrl + clic derecho arrastrando = EMPUJARLO
  - Cambia POSE para ver otras posturas: STAND, SIT, FOLD
"""
import pathlib, time
import mujoco, mujoco.viewer

POSE = "STAND"          # <- prueba "SIT" o "FOLD"

root = pathlib.Path(__file__).resolve().parent.parent
m = mujoco.MjModel.from_xml_path(str(root / "robot" / "scene.xml"))
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, m.key(POSE).id)
print(f"Robot con {m.nu} motores. Pose: {POSE}. Cierra la ventana para salir.")
with mujoco.viewer.launch_passive(m, d) as v:
    while v.is_running():
        mujoco.mj_step(m, d)
        v.sync()
        time.sleep(m.opt.timestep)
