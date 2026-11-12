"""NIVEL 3 - De recien nacido a bien entrenado.
El MISMO robot con el MISMO entrenamiento guardado en distintos momentos.
Cambia NIVEL y mira como se mueve. Pide andar con la flecha arriba
(en la TERMINAL, no en el visor). Empuja con Ctrl + clic derecho. Q = salir.
"""
import pathlib, subprocess, sys

NIVEL = 0     # <- prueba 0, 1, 2, 3, 4 y 5

CEREBROS = {
    0: "policies/progresion_0_recien_nacido.onnx",  # sin entrenar: se cae
    1: "policies/progresion_1_quieto.onnx",         # poco entrenado: no avanza
    2: "policies/progresion_2_tambaleante.onnx",    # avanza, pero se desvia
    3: "policies/progresion_3_bien.onnx",           # avanza bien
    4: "policies/progresion_4_mejor.onnx",          # el que mas avanza
    5: "policies/alpha_walking.onnx",               # el oficial
}

root = pathlib.Path(__file__).resolve().parent.parent
cmd = [sys.executable, "scripts/infer_policy.py",
       "--walking", CEREBROS[NIVEL],
       "--standing", "policies/alpha_stand.onnx",
       "--new-cmd-obs"]
print("Cerebro:", CEREBROS[NIVEL])
subprocess.run(cmd, cwd=root)
