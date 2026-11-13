"""NIVEL 1 - El robot y la escena POR DENTRO: lo que hay escrito en los XML, dibujado encima del robot.

Ya has visto las piezas sueltas (n1_03). Aqui las ves MONTADAS, y puedes encender capas para ver lo que normalmente no se ve:
   - las ARTICULACIONES (donde gira cada pieza)           - los MOTORES (uno por articulacion: son los 14 numeros que da el cerebro)
   - el CENTRO DE MASA (de donde cuelga el peso)          - las INERCIAS (cuanto cuesta girar cada pieza)
   - los EJES de cada pieza                               - las piezas de COLISION (con lo que el simulador calcula los choques)
Esas piezas de colision son mas simples que las bonitas: el simulador no calcula los choques sobre la malla de 20.000 triangulos.

El robot esta en  robot/robot_groundcontact.xml  y el mundo en  robot/scene.xml  (guia con lineas: robot/GUIA_DE_LECTURA.md).

COMO USARLO: pulsa F5. Se abre el visor 3D con el robot QUIETO (para poder mirarlo bien). En la terminal sale el arbol de piezas del XML.
   Raton: izquierda = girar | derecha = mover | rueda = acercar.   Cierra la ventana para salir.
   Cambia un valor de abajo, guarda con Ctrl+S, cierra la ventana y lanza otra vez.
"""
import pathlib, sys, time
import mujoco, mujoco.viewer

# ============================ PARAMETROS ============================

# Que mundo se carga (archivos de robot/): "scene.xml" (el normal), "scene_ball.xml" (con una pelota) o "scene_rollers.xml" (el robot con ruedas).
#   AFECTA A: el robot y el suelo que ves. Cada uno es un XML distinto: abrelo en VS Code y compara.
ESCENA = "scene.xml"

# La postura guardada con la que empieza: "STAND" (de pie), "SIT" (sentado), "FOLD" (plegado) o "INIT" (todo a cero).
#   AFECTA A: como esta colocado el robot. Salen del <keyframe> del final de scene.xml.
POSE = "STAND"

# Que capas se dibujan. Pon las que quieras: "articulaciones", "motores", "centro_de_masa", "inercias", "ejes", "colisiones", "transparente".
#   AFECTA A: solo a lo que ves, no a la fisica. Prueba primero ["articulaciones", "motores"] y despues ["colisiones"].
MOSTRAR = ["articulaciones", "motores", "centro_de_masa"]

# ¿El robot esta quieto (False) o la fisica funciona (True)? Con la fisica encendida, sin cerebro, se cae en menos de 1 s (como en n0_00).
#   AFECTA A: si puedes mirarlo con calma o lo ves caer. Empieza en False.
FISICA = False

# ¿Imprimir en la terminal el arbol de piezas del XML (cada pieza, su articulacion y cuanto puede girar)?
IMPRIMIR_ARBOL = True

# ====================================================================

robot = pathlib.Path(__file__).resolve().parent.parent / "robot"
if not (robot / ESCENA).exists():
    raise SystemExit(f"No existe {ESCENA}. Opciones: " + ", ".join(sorted(f.name for f in robot.glob('scene*.xml'))))
m = mujoco.MjModel.from_xml_path(str(robot / ESCENA))
d = mujoco.MjData(m)
posturas = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_KEY, i) for i in range(m.nkey)]
if POSE in posturas:
    mujoco.mj_resetDataKeyframe(m, d, m.key(POSE).id)
else:
    print(f"\nAVISO: {ESCENA} no trae la postura {POSE!r} ({'solo trae: ' + ', '.join(posturas) if posturas else 'no trae ninguna postura guardada'}); se usa la postura por defecto.")
mujoco.mj_forward(m, d)

if IMPRIMIR_ARBOL:
    print(f"\nEL ARBOL DE {ESCENA}: {m.nbody - 1} piezas (<body>), {m.njnt} articulaciones (<joint>), {m.nu} motores (<actuator>)\n")
    print("Cada pieza cuelga de otra (sangria). Lo que hay entre corchetes es su articulacion y lo que puede girar, en grados.\n")
    motor_de = {m.actuator_trnid[i][0]: mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for i in range(m.nu)}
    for b in range(1, m.nbody):
        nivel, p = 0, b
        while m.body_parentid[p] != 0:
            p = m.body_parentid[p]
            nivel += 1
        nombre = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b)
        art = ""
        for j in range(m.body_jntadr[b], m.body_jntadr[b] + m.body_jntnum[b]):
            jn = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j)
            if m.jnt_type[j] == mujoco.mjtJoint.mjJNT_FREE:
                art += "  [libre: el robot puede ir a donde sea]"
            else:
                lo, hi = (m.jnt_range[j] * 180 / 3.14159265).round(0)
                art += f"  [{jn}: de {lo:.0f} a {hi:.0f} grados{', con motor' if j in motor_de else ''}]"
        print("   " * nivel + "- " + (nombre or f"pieza{b}") + art)
    print("\nBuscalas en robot/robot_groundcontact.xml con Ctrl+F: cada una es un <body name=...> y su articulacion esta justo debajo.\n")

CAPAS = {"articulaciones": mujoco.mjtVisFlag.mjVIS_JOINT, "motores": mujoco.mjtVisFlag.mjVIS_ACTUATOR,
         "centro_de_masa": mujoco.mjtVisFlag.mjVIS_COM, "inercias": mujoco.mjtVisFlag.mjVIS_INERTIA,
         "transparente": mujoco.mjtVisFlag.mjVIS_TRANSPARENT}
desconocidas = [c for c in MOSTRAR if c not in list(CAPAS) + ["ejes", "colisiones"]]
if desconocidas:
    raise SystemExit(f"Capas que no existen: {desconocidas}. Opciones: articulaciones, motores, centro_de_masa, inercias, ejes, colisiones, transparente")

prueba = "--prueba" in sys.argv
with mujoco.viewer.launch_passive(m, d) as v:
    for nombre, flag in CAPAS.items():
        v.opt.flags[flag] = 1 if nombre in MOSTRAR else 0
    if "ejes" in MOSTRAR:
        v.opt.frame = mujoco.mjtFrame.mjFRAME_BODY
    if "colisiones" in MOSTRAR:
        v.opt.geomgroup[2] = 0      # se apagan las piezas bonitas (grupo 2)...
        v.opt.geomgroup[3] = 1      # ...y se encienden las de colision (grupo 3)
    t0 = time.time()
    while v.is_running() and not (prueba and time.time() - t0 > 4):
        if FISICA:
            for _ in range(5):
                mujoco.mj_step(m, d)
        else:
            mujoco.mj_forward(m, d)
        v.sync()
        time.sleep(0.01)
