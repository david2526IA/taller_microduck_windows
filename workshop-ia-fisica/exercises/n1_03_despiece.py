"""NIVEL 1 - Etapa 1: el despiece. Todas las piezas 3D que forman al Microduck, sueltas y en fila.

Cada pieza del robot es un archivo STL (una malla de triangulos) en  robot/assets/ . Aqui las ves TODAS a la vez, colocadas en una
cuadricula, para entender de que esta hecho el pato antes de verlo montado. Despues, en robot/robot_groundcontact.xml (el modelo del
robot en XML) esas mismas piezas se montan como un ARBOL: cada una cuelga de otra a traves de una articulacion.

COMO USARLO: pulsa F5. Se abre el visor 3D.
   Raton: izquierda = girar | derecha = mover | rueda = acercar.   Cierra la ventana para salir.
   Pulsa W en el visor para ver la malla de triangulos de cada pieza.
En la terminal sale la lista: el numero de cada pieza, su nombre y en que fila y columna esta. Para mirar una sola con detalle: n1_01_ver_pieza.py.
"""
import math, pathlib
import numpy as np
import mujoco, mujoco.viewer

# ============================ PARAMETROS ============================

# Cuantas piezas por fila.
#   AFECTA A: la forma de la cuadricula. Con 43 piezas, 7 da una cuadricula casi cuadrada; prueba 4 o 10.
COLUMNAS = 7

# Que piezas enseñar: None = todas, o una lista de nombres sin .stl, por ejemplo ["foot_left", "foot_right", "ankle_left"].
#   AFECTA A: lo que ves. Util para comparar solo unas pocas piezas (por ejemplo, el pie izquierdo y el derecho).
PIEZAS = None

# ¿Verlas todas del MISMO tamaño? True = cada pieza se agranda o se encoge hasta ocupar lo mismo (asi se ve el detalle de las diminutas).
#   False = a escala real: la carcasa de la cabeza es enorme y los tornillos casi no se ven. El tamaño real siempre sale en la tabla.
#   AFECTA A: solo a lo que ves, no a la fisica ni al robot.
NORMALIZAR = True

# ====================================================================

assets =pathlib.Path(__file__).resolve().parent.parent / "robot" / "assets"
disponibles = sorted(f.stem for f in assets.glob("*.stl"))
nombres = disponibles if PIEZAS is None else list(PIEZAS)
faltan = [n for n in nombres if n not in disponibles]
if faltan:
    raise SystemExit(f"No existen: {faltan}. Piezas disponibles:\n  " + "\n  ".join(disponibles))

# 1) se compilan las mallas una vez para medir cuanto ocupa cada pieza (MuJoCo las recoloca en su centro de masa)
medir = "<mujoco><compiler meshdir='%s'/><asset>%s</asset><worldbody/></mujoco>" % (
    assets.as_posix(), "".join(f"<mesh name='m{i}' file='{n}.stl'/>" for i, n in enumerate(nombres)))
mm = mujoco.MjModel.from_xml_string(medir)
centros, tamanos = [], []
for i in range(len(nombres)):
    v = mm.mesh_vert[mm.mesh_vertadr[i]:mm.mesh_vertadr[i] + mm.mesh_vertnum[i]]
    centro_local = (v.min(0) + v.max(0)) / 2
    rot = np.zeros(9)
    mujoco.mju_quat2Mat(rot, mm.mesh_quat[i])
    centros.append(mm.mesh_pos[i] + rot.reshape(3, 3) @ centro_local)      # centro de la pieza en las coordenadas originales del STL
    tamanos.append(float((v.max(0) - v.min(0)).max()))

# 2) se colocan en una cuadricula, separadas lo justo para que no se solapen
OBJETIVO = 0.06                                              # tamaño con el que se ven todas si NORMALIZAR (6 cm)
escalas = [(OBJETIVO / t if NORMALIZAR else 1.0) for t in tamanos]
paso = (OBJETIVO if NORMALIZAR else max(tamanos)) * 1.3
filas = math.ceil(len(nombres) / COLUMNAS)
colores = [(0.95, 0.6, 0.15), (0.25, 0.6, 0.85), (0.3, 0.75, 0.45), (0.85, 0.35, 0.4), (0.7, 0.55, 0.85)]
geoms, listado = [], []
for i, n in enumerate(nombres):
    fila, col = divmod(i, COLUMNAS)
    destino = np.array([col * paso, -fila * paso, 0.0])
    pos = destino - centros[i] * escalas[i]
    r, g, b = colores[i % len(colores)]
    geoms.append(f"<geom type='mesh' mesh='m{i}' pos='{pos[0]:.5f} {pos[1]:.5f} {pos[2]:.5f}' rgba='{r} {g} {b} 1'/>")
    listado.append((i + 1, n, fila + 1, col + 1, tamanos[i]))

ancho, alto = (min(COLUMNAS, len(nombres)) - 1) * paso, (filas - 1) * paso
xml = f"""<mujoco>
  <compiler meshdir="{assets.as_posix()}"/>
  <statistic center="{ancho / 2:.4f} {-alto / 2:.4f} 0" extent="{max(ancho, alto, paso) * 0.95:.4f}"/>
  <visual><global azimuth="90" elevation="-60"/><headlight ambient="0.55 0.55 0.55" diffuse="0.7 0.7 0.7"/></visual>
  <asset>{''.join(f"<mesh name='m{i}' file='{n}.stl' scale='{escalas[i]:.5f} {escalas[i]:.5f} {escalas[i]:.5f}'/>" for i, n in enumerate(nombres))}</asset>
  <worldbody>
    <light pos="{ancho / 2:.3f} {-alto / 2:.3f} 1" dir="0 0 -1" directional="true"/>
    {''.join(geoms)}
  </worldbody>
</mujoco>"""
m = mujoco.MjModel.from_xml_string(xml)

print(f"\nEL DESPIECE: {len(nombres)} piezas en {filas} filas x {COLUMNAS} columnas. Cierra la ventana para salir.\n")
print(" nº | pieza                         | fila,col | tamaño (cm)")
for n_, nom, f_, c_, t_ in listado:
    print(f" {n_:2d} | {nom:29s} | {f_:2d},{c_:<2d}    | {t_ * 100:5.1f}")
print("\nSigue: abre robot/robot_groundcontact.xml en VS Code y busca estas piezas: las encontraras como <mesh> y colgando unas de otras (<body>).")
mujoco.viewer.launch(m)
