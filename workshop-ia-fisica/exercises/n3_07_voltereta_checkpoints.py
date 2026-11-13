"""NIVEL 3 - LA VOLTERETA: ve como aprende un robot, checkpoint a checkpoint.

QUE ES UN CHECKPOINT: mientras un robot entrena, cada cierto numero de rondas se GUARDA una copia de su cerebro. Cada copia es un
checkpoint. Asi puedes ver al MISMO robot en distintos momentos de su aprendizaje, como fotos de un album.

AQUI: la voltereta hacia delante (roulade) del Microduck. Es una habilidad SENCILLA de describir ("dar una vuelta y acabar de pie") y
dificil de aprender. Hay 9 checkpoints de un entrenamiento REAL de 20.750 rondas (en una GPU). Cambia CHECKPOINT y mira.

COMO USARLO (3 pasos):
  1. Cambia el numero de CHECKPOINT (abajo), guarda con Ctrl+S y pulsa F5. Se abre la ventana del robot.
  2. Pulsa la tecla  R  en la TERMINAL (no en la ventana del robot): el robot intenta la voltereta.
  3. Pulsa  Q  para salir. Cierra la ventana del robot antes de probar otro checkpoint.

Controles (en la TERMINAL):  R = voltereta | flechas = andar | Y = sentarse | Q = salir | Ctrl + clic derecho sobre el robot = empujarlo
"""
import pathlib, subprocess, sys

# ============================ PARAMETROS ============================

# Que checkpoint ves: el numero de RONDA de entrenamiento en el que se guardo.
#   AFECTA A: lo bien (o mal) que hace la voltereta. Lo que se ha MEDIDO en simulacion (10 intentos cada uno, voltereta completa y de pie):
#       0  .......... 0 de 10   recien nacido: no sabe nada, se queda quieto
#       500  ........ 0 de 10   todavia nada
#       750  ........ 10 de 10  ¡aparece la voltereta! (ya a las 750 rondas)
#       1250  ....... 9 de 10   casi siempre
#       3000  ....... 4 de 10   ¡se vuelve irregular! (a veces gira, a veces se queda quieto)
#       7000  ....... 5 de 10   sigue irregular (entrenar mas no siempre mejora)
#       11000  ...... 10 de 10  estable
#       20000  ...... 3 de 10   ¡el ultimo guardado no siempre es el mejor!
#       20750  ...... 10 de 10  el final del entrenamiento
#   Prueba primero 0, luego 750, luego 7000 y 11000. ¿Notas la diferencia? Para medirlo con numeros: n3_08_voltereta_medir.py
CHECKPOINT = 750

# ---------- PERTURBACIONES (opcional, para romper el mundo; None = sin tocar) ----------
VOLTAJE_BATERIA = None    # Prueba 6.5 (bateria baja). Normal: 7.4.  AFECTA A: la fuerza de los motores.
RETRASO_MOTORES = None    # Prueba (2, 4): los motores obedecen con retraso. AFECTA A: lo bien que reacciona el cerebro.
POTENCIA_MOTORES = None   # Prueba 0.7: motores mas debiles. Normal: 1.0.

# ====================================================================

DISPONIBLES = (0, 500, 750, 1250, 3000, 7000, 11000, 20000, 20750)
if CHECKPOINT not in DISPONIBLES:
    raise SystemExit(f"CHECKPOINT = {CHECKPOINT} no existe. Elige uno de: {', '.join(map(str, DISPONIBLES))}")

root = pathlib.Path(__file__).resolve().parent.parent
voltereta = f"policies/voltereta/voltereta_{CHECKPOINT:05d}.onnx"

cmd = [sys.executable, "scripts/infer_policy.py",
       "--walking", "policies/alpha_walking.onnx",      # el cerebro de andar (para moverte)
       "--standing", "policies/alpha_stand.onnx",       # el cerebro de estar de pie
       "--roulade", voltereta,                          # EL CHECKPOINT QUE ESTAS PROBANDO (tecla R)
       "--new-cmd-obs"]                                 # formato de entrada que esperan estos cerebros
if VOLTAJE_BATERIA is not None:
    cmd += ["--vin", str(VOLTAJE_BATERIA)]
if RETRASO_MOTORES is not None:
    cmd += ["--delay", *map(str, RETRASO_MOTORES)]
if POTENCIA_MOTORES is not None:
    cmd += ["--action-scale", str(POTENCIA_MOTORES)]

print(f"\nCHECKPOINT {CHECKPOINT}: pulsa R en esta terminal para la voltereta (Q para salir).\n")
subprocess.run(cmd, cwd=root)
