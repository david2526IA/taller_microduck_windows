"""NIVEL 3 - ¡El Microduck PATINA! Mismo robot, ahora con ruedas, y un cerebro distinto.
Pulsa las teclas en la TERMINAL (no en el visor). Q = salir.

  Flecha ARRIBA   = acelerar (cada pulsacion un poco mas rapido)
  Flecha ABAJO    = frenar (si sigues, va marcha atras)
  Flechas IZQ/DER = girar            (o A / E)
  Espacio         = soltar el acelerador (deja de empujar, sigue rodando)
  Ctrl + clic derecho arrastrando sobre el robot = EMPUJARLO

Retos: 1) llega a la velocidad maxima  2) dibuja un 8  3) empujalo mientras patina  4) frena en seco.
Abajo puedes romper el mundo (bateria, retraso, motores) y ver como cambia el patinaje.
"""
import pathlib, subprocess, sys

PATINAR = "policies/roller.onnx"          # cerebro: rodar y girar
AGACHARSE = "policies/roller_crouch.onnx"  # cerebro: quedarse agachado y quieto sobre las ruedas

# --- PERTURBACIONES (None = sin tocar) ---
VOLTAJE_BATERIA = None   # prueba 6.5 (bateria baja)
RETRASO_MOTORES = None   # prueba (2, 4): los motores obedecen tarde
POTENCIA_MOTORES = None  # prueba 0.7: motores mas debiles

root = pathlib.Path(__file__).resolve().parent.parent
cmd = [sys.executable, "scripts/infer_policy.py", "--roller",
       "--walking", PATINAR, "--standing", AGACHARSE, "--new-cmd-obs"]
if VOLTAJE_BATERIA is not None:
    cmd += ["--vin", str(VOLTAJE_BATERIA)]
if RETRASO_MOTORES is not None:
    cmd += ["--delay", *map(str, RETRASO_MOTORES)]
if POTENCIA_MOTORES is not None:
    cmd += ["--action-scale", str(POTENCIA_MOTORES)]

print("Lanzando:", " ".join(cmd))
subprocess.run(cmd, cwd=root)
