#!/usr/bin/env python3
"""Comprueba que el PC esta listo para el workshop.  Uso:  python check_setup.py [--viewer]"""
import importlib, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
OK, KO = "[ OK ]", "[FALLA]"
fallos = 0

def check(nombre, cond, ayuda=""):
    global fallos
    print(f"{OK if cond else KO} {nombre}" + ("" if cond else f"  ->  {ayuda}"))
    fallos += 0 if cond else 1

v = sys.version_info
check(f"Python {v.major}.{v.minor}", (v.major, v.minor) == (3, 12),
      "se necesita Python 3.12 (instalar con: winget install Python.Python.3.12)")

for mod in ["mujoco", "onnxruntime", "numpy", "bam"]:
    try:
        importlib.import_module(mod); check(f"import {mod}", True)
    except Exception as e:
        check(f"import {mod}", False, f"pip install -r requirements.txt  ({type(e).__name__})")

try:
    import inspect, bam.mujoco as _bm
    check("bam: version correcta del proyecto",
          "vin_drop_gain" in inspect.signature(_bm.MujocoController.__init__).parameters,
          "reinstalar: pip install --force-reinstall --no-deps -r requirements.txt")
except Exception as e:
    check("bam: version correcta del proyecto", False, str(e))

scene = ROOT / "robot" / "scene.xml"
check("robot/scene.xml existe", scene.exists(), "falta la carpeta robot/ (git clone incompleto)")
check("mallas STL del robot", len(list((ROOT / "robot" / "assets").glob("*.stl"))) > 10, "falta robot/assets")

onnx = sorted((ROOT / "policies").glob("*.onnx"))
check(f"politicas ONNX en policies/ ({len(onnx)})", len(onnx) > 0,
      "ejecutar: python tools/prepare_assets.py  (una vez, con internet)")

try:
    import mujoco
    m = mujoco.MjModel.from_xml_path(str(scene)); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("STAND").id)
    for _ in range(100): mujoco.mj_step(m, d)
    check(f"MuJoCo simula el robot ({m.nu} motores)", m.nu == 14)
except Exception as e:
    check("MuJoCo simula el robot", False, str(e))

if onnx:
    try:
        import onnxruntime as ort
        s = ort.InferenceSession(str(onnx[0]))
        check(f"ONNX Runtime carga {onnx[0].name}", True)
    except Exception as e:
        check("ONNX Runtime carga una politica", False, str(e))

if "--viewer" in sys.argv:
    import mujoco.viewer, time
    print("Abriendo visor 5 s...")
    with mujoco.viewer.launch_passive(m, d) as viz:
        t0 = time.time()
        while viz.is_running() and time.time() - t0 < 5:
            mujoco.mj_step(m, d); viz.sync(); time.sleep(0.002)
    check("Visor de MuJoCo", True)

print("\n" + ("TODO LISTO" if fallos == 0 else f"{fallos} problema(s): revisa las lineas [FALLA]"))
sys.stdout.flush()
if "--viewer" in sys.argv:
    os._exit(1 if fallos else 0)  # evita un cierre con 'segmentation fault' de GLFW al apagar Python con el visor abierto
sys.exit(1 if fallos else 0)
