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
    with contextlib.redirect_stdout(io.StringIO()):           # el mundo cambia de verdad: en la Luna la pelota llega mas lejos
        env.set_mundo(1.62)
        x_luna = env.step(0.9, "kick_right")[0]
    check(f"mundos distintos (Luna: la misma patada llega a x={x_luna:.2f} m)", x_luna > x + 0.5)
except Exception as e:
    check("entorno de entrenamiento de la patada", False, str(e)[:160])

# el laboratorio de mundos (n1_02): todos los mundos predefinidos y los cuatro tipos de objeto compilan
try:
    import importlib.util
    s = importlib.util.spec_from_file_location("n1_02", RAIZ / "exercises_rayuela" / "n1_02_tu_escena.py")
    lab = importlib.util.module_from_spec(s)
    s.loader.exec_module(lab)
    lab.OBJETOS = [dict(tipo="caja"), dict(tipo="rampa", angulo=8), dict(tipo="esfera", tam=(0.04,), fijo=False), dict(tipo="cilindro", tam=(0.03, 0.1))]
    for mundo in lab.MUNDOS:
        lab.MUNDO = mundo
        sp = mujoco.MjSpec.from_file(str(ofi / "src/mjlab_microduck/robot/microduck/scene.xml"))
        lab.editar_escena(sp)
        sp.compile()
    # en el mundo NORMAL el ejercicio no debe cambiar la fisica (un ajuste mal puesto hacia que la pelota se pasara de la casilla)
    lab.MUNDO, lab.OBJETOS = None, []
    escena = str(ofi / "src/mjlab_microduck/robot/microduck/scene.xml")
    original = mujoco.MjSpec.from_file(escena).compile()
    sp = mujoco.MjSpec.from_file(escena)
    lab.editar_escena(sp)
    editado = sp.compile()
    for nombre in ("floor", "left_foot_collision", "right_foot_collision", "ball_geom"):
        i = mujoco.mj_name2id(original, mujoco.mjtObj.mjOBJ_GEOM, nombre)
        j = mujoco.mj_name2id(editado, mujoco.mjtObj.mjOBJ_GEOM, nombre)
        if i >= 0:
            assert (original.geom_friction[i] == editado.geom_friction[j]).all() and original.geom_priority[i] == editado.geom_priority[j]                 and (original.geom_size[i] == editado.geom_size[j]).all(), f"el mundo normal de n1_02 cambia la fisica de {nombre}"
    check(f"laboratorio de mundos ({len(lab.MUNDOS)} mundos y 4 tipos de objeto)", True)
except Exception as e:
    check("laboratorio de mundos (n1_02)", False, str(e)[:160])

# el robot en XML y sus piezas STL (lo que ensenan n1_03 y n1_04)
try:
    carpeta = RAIZ / "workshop-ia-fisica" / "robot"
    stl = sorted((carpeta / "assets").glob("*.stl"))
    mujoco.MjModel.from_xml_string("<mujoco><compiler meshdir='%s'/><asset>%s</asset><worldbody/></mujoco>" % (
        (carpeta / "assets").as_posix(), "".join(f"<mesh name='m{i}' file='{p.name}'/>" for i, p in enumerate(stl))))
    rob = mujoco.MjModel.from_xml_path(str(carpeta / "scene.xml"))
    check(f"el robot en XML: {len(stl)} piezas STL, {rob.nbody - 1} piezas montadas y {rob.nu} motores", len(stl) == 43 and rob.nu == 14)
except Exception as e:
    check("el robot en XML y sus piezas STL", False, str(e)[:160])

# la voltereta: checkpoints reales (0 = no gira, 750 = gira y acaba de pie)
try:
    import voltereta_env
    with contextlib.redirect_stdout(io.StringIO()):
        venv = voltereta_env.VolteretaEnv()
        g0 = venv.probar(RAIZ / "workshop-ia-fisica" / "policies" / "voltereta" / "voltereta_00000.onnx")
        g750 = venv.probar(RAIZ / "workshop-ia-fisica" / "policies" / "voltereta" / "voltereta_00750.onnx")
    check(f"voltereta: checkpoint 0 no gira ({g0[0]:.0f} gr) y el 750 si ({g750[0]:.0f} gr, de pie: {g750[1]})", g0[0] < 60 and g750[0] > 300 and g750[1])
except Exception as e:
    check("voltereta (checkpoints)", False, str(e)[:160])

# configurar un entrenamiento real: se leen las recompensas oficiales, se generan los paquetes y el parche de pesos se aplica y compila
try:
    import entrenamiento, py_compile, shutil, subprocess, tempfile
    tmp = pathlib.Path(tempfile.mkdtemp())
    for caso, c in entrenamiento.CASOS.items():
        assert entrenamiento.leer_recompensas(caso), f"sin recompensas: {caso}"
        entrenamiento.generar_paquete(caso, tmp / caso, constantes=None, pesos={entrenamiento.leer_recompensas(caso)[0][0]: ("*", 0.5)})
        if c["cfg"]:
            proj = tmp / (caso + "_proj")
            (proj / pathlib.Path(c["cfg"]).parent).mkdir(parents=True)
            shutil.copy(entrenamiento.OFICIAL / c["cfg"], proj / c["cfg"])
            r = subprocess.run([sys.executable, str(tmp / caso / "2_aplicar_pesos.py"), str(proj)], capture_output=True, text=True)
            assert r.returncode == 0, r.stderr[-200:]
    entrenamiento.generar_paquete("obstaculos", tmp / "curriculo", partir_de="model_9999.pt")
    assert "--agent.load-checkpoint model_9999.pt" in (tmp / "curriculo" / "4_entrenar.sh").read_text(encoding="utf-8")
    check(f"paquetes de entrenamiento ({len(entrenamiento.CASOS)} casos: voltereta, rayuela, patines, obstaculos, cuerda)", True)
    check("curriculo entre politicas: el paquete parte de un checkpoint (--agent.load-checkpoint)", True)
except Exception as e:
    check("paquetes de entrenamiento", False, str(e)[:160])

# politicas para terreno irregular (Hugging Face) y el circuito de obstaculos
try:
    import obstaculos
    check("cerebros rough_walk_e y rough_walk_g", all(obstaculos.CEREBROS[c].exists() for c in obstaculos.CEREBROS), "faltan en windows/politicas")
except Exception as e:
    check("circuito de obstaculos", False, str(e)[:160])

# preparar el sim-to-real: el contrato de un cerebro
try:
    import sim2real
    check("contrato de un .onnx (sim-to-real)", all(ok for _, ok, _ in sim2real.contrato("alpha_walking")), "falla alguna comprobacion")
except Exception as e:
    check("sim-to-real", False, str(e)[:160])

# el duelo de la cuerda: escena de dos patos (la genera el constructor oficial), motores BAM y el cerebro entrenado
try:
    import contextlib, io
    import duelo
    check("cerebro del duelo (duelo2.onnx)", duelo.POLITICA_DUELO.exists(), "falta windows/politicas/duelo2.onnx")
    import numpy as _np, onnxruntime as _ort
    _car = pathlib.Path(duelo.POLITICA_DUELO).parent / "duelo"
    _et = sorted(_car.glob("duelo_*.onnx"))
    _o = _np.linspace(-1, 1, 61, dtype=_np.float32)[None, :]
    _f = lambda p: _ort.InferenceSession(str(p)).run(None, {"obs": _o})[0]
    check(f"etapas del duelo ({len(_et)} onnx; la 6027 == duelo2.onnx)", len(_et) == 9 and float(abs(_f(_car / "duelo_06027.onnx") - _f(duelo.POLITICA_DUELO)).max()) < 1e-5, "faltan etapas en windows/politicas/duelo")
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
