"""NIVEL 3 - El robot CON cerebro.
Lanza la demo con IA. Es el comando largo de siempre, pero explicado:
cada cerebro (.onnx) hace una cosa distinta.

Controles (pulsalos en la TERMINAL, no en el visor):
  Flechas = velocidad | A / E = girar | Y = sentarse/levantarse | R = voltereta | Q = salir
  Ctrl + clic derecho arrastrando sobre el robot = EMPUJARLO

El suelo se cambia en robot/scene.xml (friction="1 ...").
"""
import pathlib, subprocess, sys

# --- LOS CEREBROS: cada fichero .onnx es una red entrenada para una tarea ---
ANDAR   = "policies/alpha_walking.onnx"    # camina siguiendo la velocidad que pidas
QUIETO  = "policies/alpha_stand.onnx"      # se mantiene de pie sin moverse
SENTARSE = "policies/alpha_sitstand.onnx"  # tecla Y: se sienta y se levanta
VOLTERETA = "policies/roulade.onnx"        # tecla R: voltereta

# --- PERTURBACIONES: pon valores para romper el mundo (None = sin tocar) ---
VOLTAJE_BATERIA = None   # prueba 6.5 (bateria baja). Normal: 7.4
RETRASO_MOTORES = None   # prueba (2, 4): los motores obedecen tarde
POTENCIA_MOTORES = None  # prueba 0.7: motores mas debiles. Normal: 1.0

root = pathlib.Path(__file__).resolve().parent.parent

cmd = [sys.executable, "scripts/infer_policy.py",
       "--walking", ANDAR,
       "--standing", QUIETO,
       "--sitstand", SENTARSE,
       "--roulade", VOLTERETA,
       "--new-cmd-obs"]          # formato de entrada que esperan estas politicas
if VOLTAJE_BATERIA is not None:
    cmd += ["--vin", str(VOLTAJE_BATERIA)]
if RETRASO_MOTORES is not None:
    cmd += ["--delay", *map(str, RETRASO_MOTORES)]
if POTENCIA_MOTORES is not None:
    cmd += ["--action-scale", str(POTENCIA_MOTORES)]

print("Lanzando:", " ".join(cmd))
subprocess.run(cmd, cwd=root)
