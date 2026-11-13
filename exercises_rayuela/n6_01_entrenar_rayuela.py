"""CONFIGURA TU ENTRENAMIENTO · CASO 1 · LA RAYUELA: aprender a patear la pelota a una casilla.

Esto es lo que se hace ANTES de pulsar "entrenar" en un entrenamiento real con mjlab (en un PC sin GPU no se puede entrenar con mjlab,
pero TODO lo demas si se puede preparar):
   1. elegir la TAREA            (aqui: Mjlab-BallKickSpeed-Right-Flat-MicroDuck, y su gemela del pie izquierdo)
   2. leer la RECOMPENSA real    (se imprime sola: terminos y pesos del fichero oficial)
   3. cambiar lo que quieras     (pesos, constantes de la tarea, rondas, robots a la vez, tasa de aprendizaje...)
   4. generar tu PAQUETE         (scripts listos para lanzar en Ubuntu con GPU, o en una GPU de la nube) en mi_entrenamiento/rayuela/

COMO USARLO: ejecuta (F5) SIN tocar nada y lee la salida. Despues cambia UN valor, guarda y vuelve a ejecutar: veras cambiar el
comando y los scripts. Lo que SI puedes entrenar de verdad aqui, en CPU, es la version pequena de esta misma tarea: n3_05_entrena_la_patada.py.
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# ---------- 1. CUANTA EXPERIENCIA ----------
# Robots que entrenan A LA VEZ en la GPU (4096 es lo habitual en una GPU de gama alta).
#   AFECTA A: la experiencia por minuto y la memoria de la GPU. Si no cabe, baja a 2048 o 1024. MEDIDO (levantarse, 100 rondas):
#   con 256 robots la recompensa final fue 6,1 frente a 25,4 con 4096: pocos robots = mucho mas lento.
NUM_ENVS = 4096

# Rondas de entrenamiento (cada una = probar, puntuar y ajustar con miles de pasos de simulacion).
#   AFECTA A: cuanto aprende. OJO: esta tarea tiene un CURRICULO que sube los pesos de la recompensa por etapas hasta la ronda 1.000
#   (en el fichero: "step 1000 * 24"). Con menos de 1.000 rondas el curriculo no llega a sus pesos finales. Prueba 300 y compara.
ITERACIONES = 1500

# Cada cuantas rondas se guarda el cerebro (los checkpoints). Sirven para ver la progresion, como n3_01.
GUARDAR_CADA = 100

# ---------- 2. EL ALGORITMO PPO (None = el de la tarea) ----------
# Tamano de cada ajuste. MEDIDO en entrenar/experimentos.sh (tarea de levantarse, 100 rondas, recompensa final):
#   base 25,4 | learning rate 0.00005 -> 8,8 (casi no aprende) | 0.01 -> se descontrola (recompensa de -4 mil millones).
LEARNING_RATE = None
# Premio por seguir explorando. MEDIDO en esos mismos experimentos: con 0.1 la recompensa final fue -108 (explora tanto que no aprende).
ENTROPIA = None
# Cuanto "piensa" en el futuro (0.8 = miope, 0.99 = largo plazo). Una patada dura 2 s en la Rayuela: no necesita pensar mucho mas alla.
#   MEDIDO: gamma 0.8 dio 27,3 frente a 25,4 de la base en la tarea de levantarse: aqui apenas importa.
GAMMA = None

# ---------- 3. LA RECOMPENSA ----------
# Pesos de terminos de recompensa a cambiar: {"termino": valor} FIJA el peso | {"termino": ("*", 0.5)} lo MULTIPLICA.
#   AFECTA A: lo que el robot "quiere". ATENCION: ball_forward_velocity, ball_speed_gaussian, ball_aim y kick_settled_stand los gobierna
#   el currículo (cambian por etapas); para esos usa CONSTANTES. Aqui puedes cambiar ball_speed_overshoot (castigo por pasarse de velocidad).
#   Ejemplo:  PESOS = {"ball_speed_overshoot": -8.0}
PESOS = {}

# Constantes de la tarea (se listan al ejecutar): KICK_GAUSSIAN_WEIGHT es el peso FINAL de "acertar la velocidad pedida",
# KICK_AIM_WEIGHT el de "patear recto", KICK_SETTLE_WEIGHT el de "quedarse de pie despues".
#   AFECTA A: lo que premia el robot al final del entrenamiento.
#   Ejemplo:  CONSTANTES = {"KICK_AIM_WEIGHT": -4.0}   (menos castigo por patear torcido: ¿saldran patadas mas fuertes pero torcidas?)
CONSTANTES = {}

# Nombre del experimento (carpeta donde se guardan las curvas y los cerebros).
NOMBRE = "taller_rayuela"

# ====================================================================

if __name__ == "__main__":
    import entrenamiento
    entrenamiento.principal("rayuela", num_envs=NUM_ENVS, iteraciones=ITERACIONES, guardar_cada=GUARDAR_CADA, nombre=NOMBRE,
                            learning_rate=LEARNING_RATE, entropia=ENTROPIA, gamma=GAMMA, pesos=PESOS, constantes=CONSTANTES)
