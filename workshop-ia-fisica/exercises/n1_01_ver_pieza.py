"""NIVEL 1 - Etapa 1: el modelo 3D. Cada pieza del robot es una malla STL (triangulos).
Abre una pieza suelta en el visor de MuJoCo. Cambia PIEZA por otra de robot/assets/
(por ejemplo: "foot_left", "trunk_base", "top_head_shell", "upper_leg_left", "leg", "xl330").
Tambien puedes elegirla al lanzar, sin editar nada:  python exercises/n1_01_ver_pieza.py foot_left
Para cambiar de pieza hay que CERRAR la ventana y volver a lanzar (el visor no se recarga solo).
Pulsa W en el visor (o ve a Rendering) para ver la malla de triangulos. Raton: izq rotar, rueda zoom.
"""
import pathlib, sys
import mujoco, mujoco.viewer

PIEZA = "jaw"  # <- prueba otra pieza de robot/assets/

assets = pathlib.Path(__file__).resolve().parent.parent / "robot" / "assets"
if len(sys.argv) > 1:
    PIEZA = sys.argv[1].removesuffix(".stl")
if not (assets / f"{PIEZA}.stl").exists():
    nombres = sorted(f.stem for f in assets.glob("*.stl"))
    raise SystemExit(f"No existe la pieza '{PIEZA}'. Escribe el nombre exacto, sin .stl. Piezas disponibles:\n  " + "\n  ".join(nombres))
xml = f"""
<mujoco>
  <compiler meshdir="{assets.as_posix()}"/>
  <visual><global azimuth="140" elevation="-20"/></visual>
  <asset><mesh name="p" file="{PIEZA}.stl"/></asset>
  <worldbody>
    <light pos="0 0 1" dir="0 0 -1"/>
    <geom type="mesh" mesh="p" rgba="0.95 0.6 0.15 1"/>
  </worldbody>
</mujoco>"""
m = mujoco.MjModel.from_xml_string(xml)
print(f"Pieza '{PIEZA}': {m.mesh_vertnum[0]} vertices, {m.mesh_facenum[0]} triangulos. Cierra la ventana para salir.")
mujoco.viewer.launch(m)
