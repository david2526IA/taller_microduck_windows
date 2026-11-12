"""NIVEL 2 - El robot SIN cerebro.
Le damos la postura de pie y le decimos "mantenla" (control PD simple, sin IA).
Resultado: se cae solo en menos de 1 segundo. Equilibrar un biped NO se resuelve fijando una
postura: hace falta una politica que reaccione 50 veces por segundo.
Cambia FRICCION y FACTOR_MASA y comprueba si algo lo salva. Despues compara con run_demo.bat.
"""
import pathlib
import mujoco

FRICCIONES = [0.2, 1.0, 2.0]    # <- prueba otros valores
FACTOR_MASA = 1.0                # <- prueba 0.5 o 2.0
SEGUNDOS = 3.0

root = pathlib.Path(__file__).resolve().parent.parent
print(f"{'friccion':>9} | {'tiempo hasta caer':>18}")
for fr in FRICCIONES:
    m = mujoco.MjModel.from_xml_path(str(root / "robot" / "scene.xml"))
    d = mujoco.MjData(m)
    m.geom_friction[:, 0] *= fr
    m.body_mass[:] *= FACTOR_MASA
    key = m.key("STAND").id
    mujoco.mj_resetDataKeyframe(m, d, key)
    d.ctrl[:] = m.key_ctrl[key]                  # "mantén esta postura"
    t_caida = None
    for i in range(int(SEGUNDOS / m.opt.timestep)):
        mujoco.mj_step(m, d)
        if d.qpos[2] < 0.06:                     # altura del tronco < 6 cm = caido
            t_caida = i * m.opt.timestep
            break
    print(f"{fr:>9} | {(f'{t_caida:.2f} s' if t_caida else 'aguanta de pie'):>18}")
