#!/usr/bin/env python3
"""Comprueba que TODO el taller funciona en este PC (lo de la Rayuela, la cuerda, el balancin, el entrenamiento...).
Uso:  workshop-ia-fisica\\.venv\\Scripts\\python.exe check_taller.py [--viewer]
Debe acabar en TODO LISTO. Tarda unos 30 segundos."""
import os, pathlib, subprocess, sys, time

RAIZ = pathlib.Path(__file__).resolve().parent
fallos = 0


def check(nombre, cond, ayuda=""):
    global fallos
    print(f"{'[ OK ]' if cond else '[FALLA]'} {nombre}" + ("" if cond else f"  ->  {ayuda}"))
    fallos += 0 if cond else 1


v = sys.version_info
check(f"Python {v.major}.{v.minor}", (v.major, v.minor) == (3, 12), "se necesita Python 3.12 (ejecuta INSTALAR.bat)")
try:
    import cv2
    check(f"OpenCV {cv2.__version__} (vision de la Rayuela)", True)
except Exception as e:
    check("OpenCV", False, f"ejecuta INSTALAR.bat de nuevo ({type(e).__name__})")

ofi = RAIZ / "rayuela-oficial"
check("rayuela-oficial/ (repo oficial de Bravo Robots)", (ofi / "scripts" / "infer_policy.py").exists(), "falta la carpeta: git clone incompleto")
for onnx in ("alpha_walking", "alpha_standing", "ball_kick_speed_left", "ball_kick_speed_right", "roulade"):
    check(f"cerebro {onnx}.onnx", (ofi / "policies-v1" / f"{onnx}.onnx").exists(), "falta en rayuela-oficial/policies-v1")
check("cerebros de patines (roller.onnx)", (RAIZ / "workshop-ia-fisica" / "policies" / "roller.onnx").exists(), "falta en workshop-ia-fisica/policies")

try:
    import mujoco
    spec = mujoco.MjSpec.from_file(str(ofi / "src/mjlab_microduck/robot/microduck/escena_rayuela.xml"))
    m = spec.compile()
    check(f"escena de la Rayuela compila ({m.nu} motores)", m.nu == 14)
except Exception as e:
    check("escena de la Rayuela", False, str(e)[:120])

# entorno de entrenamiento + una patada de prueba (comprueba MuJoCo + BAM + cerebro ONNX a la vez)
try:
    sys.path.insert(0, str(RAIZ / "windows"))
    t = time.time()
    import contextlib, io
    import patada_env
    with contextlib.redirect_stdout(io.StringIO()):           # el codigo oficial imprime mucho al cargar
        env = patada_env.PatadaEnv()
        x, y, casilla, cayo = env.step(0.9, "kick_right")
    check(f"una patada simulada: la pelota llega a x={x:.2f} m ({time.time() - t:.0f} s)", x > 0.5 and not cayo)
except Exception as e:
    check("entorno de entrenamiento de la patada", False, str(e)[:160])

# politicas para terreno irregular (Hugging Face) y el circuito de obstaculos
try:
    import obstaculos
    check("cerebros rough_walk_e y rough_walk_g", all(obstaculos.CEREBROS[c].exists() for c in obstaculos.CEREBROS), "faltan en windows/politicas")
except Exception as e:
    check("circuito de obstaculos", False, str(e)[:160])

# el duelo de la cuerda: escena de dos patos (la genera el constructor oficial), motores BAM y el cerebro entrenado
try:
    import contextlib, io
    import duelo
    check("cerebro del duelo (duelo2.onnx)", duelo.POLITICA_DUELO.exists(), "falta windows/politicas/duelo2.onnx")
    with contextlib.redirect_stdout(io.StringIO()):
        m2, d2, ctrl, nombres = duelo.cargar_mundo(1.0, 1.0, 1.0, 1.0, 1.0)
    check(f"escena de la cuerda con motores BAM ({len(nombres)} motores, 2 patos)", len(nombres) == 28)
except Exception as e:
    check("el duelo de la cuerda", False, str(e)[:160])

if "--viewer" in sys.argv and fallos == 0:
    import mujoco.viewer
    print("Abriendo visor 5 s...")
    with mujoco.viewer.launch_passive(m, mujoco.MjData(m)) as viz:
        t0 = time.time()
        while viz.is_running() and time.time() - t0 < 5:
            viz.sync()
            time.sleep(0.02)

print("\n" + ("TODO LISTO" if fallos == 0 else f"HAY {fallos} PROBLEMA(S): enviar instalar_log.txt al ponente"))
sys.exit(1 if fallos else 0)
