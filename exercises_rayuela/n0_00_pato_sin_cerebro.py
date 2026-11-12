"""PASO 2 DE LA RUTA - EL PATO SIN CEREBRO: mira como se cae.

Le damos al Microduck la postura de pie y le ordenamos "mantenla" con un control simple (PD), sin inteligencia
artificial. Parece suficiente... y no lo es: en menos de un segundo se cae. Un robot con dos patas es como un lapiz
sobre su punta: para mantenerse hace falta REACCIONAR muchas veces por segundo a lo que va pasando. Eso es lo que
hara el cerebro en el paso siguiente.

Se abre la ventana 3D. Rueda del raton = zoom, boton izquierdo = girar la camara. Al caerse, el pato se queda
tumbado y en la terminal sale el tiempo que aguanto. Cierra la ventana para terminar.
"""
import pathlib, time
import mujoco, mujoco.viewer

# ============================ PARAMETROS ============================

# Camara lenta: 1.0 = tiempo real | 0.2 = cinco veces mas lento (ideal para VER como empieza a caerse).
#   AFECTA A: solo a lo que ves, no a la fisica.
VELOCIDAD = 0.3

# Rozamiento de los pies con el suelo, multiplicado por este numero (1.0 = normal | 0.2 = hielo | 3.0 = pegajoso).
#   AFECTA A: si los pies resbalan. Prueba 3.0: ¿se salva? (Spoiler: no, el problema no es el agarre.)
FRICCION = 1.0

# Masa de todo el robot, multiplicada por este numero (1.0 = normal | 0.5 = mitad | 2.0 = doble).
#   AFECTA A: lo facil que es caerse. Cambia el tiempo, pero no la conclusion.
FACTOR_MASA = 1.0

# Empujon inicial (m/s hacia delante) para ver si aguanta algo: 0 = ninguno.
#   AFECTA A: un pato bien equilibrado lo absorberia. Sin cerebro, ni lo intenta.
EMPUJON = 0.0

# ====================================================================

raiz = pathlib.Path(__file__).resolve().parent.parent / "workshop-ia-fisica"
m = mujoco.MjModel.from_xml_path(str(raiz / "robot" / "scene.xml"))
d = mujoco.MjData(m)
m.geom_friction[:, 0] *= FRICCION
m.body_mass[:] *= FACTOR_MASA
clave = m.key("STAND").id
mujoco.mj_resetDataKeyframe(m, d, clave)
d.ctrl[:] = m.key_ctrl[clave]                  # "mantén esta postura": sin cerebro, solo una consigna fija
d.qvel[0] = EMPUJON
mujoco.mj_forward(m, d)

print(__doc__)
t_caida = None
with mujoco.viewer.launch_passive(m, d) as visor:
    t0 = time.time()
    while visor.is_running():
        inicio = time.time()
        mujoco.mj_step(m, d)
        if t_caida is None and d.qpos[2] < 0.07:           # el tronco por debajo de 7 cm = caido
            t_caida = d.time
            print(f"\n>> SE HA CAIDO a los {t_caida:.2f} s de simulacion.  Sin cerebro no hay equilibrio.\n", flush=True)
        visor.sync()
        espera = m.opt.timestep / VELOCIDAD - (time.time() - inicio)
        if espera > 0:
            time.sleep(espera)
