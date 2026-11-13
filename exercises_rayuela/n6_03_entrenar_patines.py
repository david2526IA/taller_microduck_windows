"""CONFIGURA TU ENTRENAMIENTO · CASO 3 · LOS PATINES: el mismo robot con otro CUERPO.

Otra VERSION del problema: el robot lleva ruedas bajo los pies. La tarea sigue siendo "obedecer una orden de velocidad", pero el
contacto con el suelo cambia, asi que cambia la recompensa (ya no se premia levantar los pies) y la aleatorizacion (rozamiento de las ruedas,
centro de masa). Aqui lees la recompensa real de los patines, cambias lo que quieras y generas tu paquete en mi_entrenamiento/patines/.
En CPU puedes jugar con el cerebro de patines ya entrenado y romperlo (bateria baja, retraso de motores): n4_02_patines.py.

COMO USARLO: ejecuta (F5) sin tocar nada y lee la salida; despues cambia UN valor y vuelve a ejecutar.
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# ---------- 1. CUANTA EXPERIENCIA ----------
NUM_ENVS = 4096      # AFECTA A: experiencia por minuto y memoria de GPU (si no cabe: 2048 o 1024).
# Rondas. Los documentos oficiales de tareas con patines usan de 3.500 a 15.000 segun la tarea (con 4.096 robots). Es una referencia, no una garantia.
ITERACIONES = 3500
GUARDAR_CADA = 250

# ---------- 2. EL ALGORITMO PPO (None = el de la tarea) ----------
LEARNING_RATE = None
ENTROPIA = None
GAMMA = None

# ---------- 3. LA RECOMPENSA ----------
# {"termino": valor} FIJA el peso | {"termino": ("*", 0.5)} lo MULTIPLICA. Los terminos se listan al ejecutar.
#   AFECTA A: como patina. Ideas para predecir antes de cambiar:
#     · upright: premia el tronco vertical. Mas peso = patina mas tieso, pero ¿puede frenar bien?
#     · action_rate_l2: castiga los cambios bruscos de orden. Mas castigo = movimientos suaves (¿y mas lentos para reaccionar?)
#   Ejemplo:  PESOS = {"upright": ("*", 2.0)}
PESOS = {}

# Constantes de la tarea (se listan al ejecutar): aqui son sobre todo la ALEATORIZACION de dominio (centro de masa, orientacion del sensor IMU).
#   AFECTA A: lo robusta que sera al pasar al robot real: mas aleatorizacion = mas robusta, pero tarda mas en aprender (lo viste en n5_01).
#   Ejemplo:  CONSTANTES = {"IMU_ORIENTATION_RANDOMIZATION_ANGLE": 10.0}
CONSTANTES = {}

NOMBRE = "taller_patines"

# ====================================================================

if __name__ == "__main__":
    import entrenamiento
    entrenamiento.principal("patines", num_envs=NUM_ENVS, iteraciones=ITERACIONES, guardar_cada=GUARDAR_CADA, nombre=NOMBRE,
                            learning_rate=LEARNING_RATE, entropia=ENTROPIA, gamma=GAMMA, pesos=PESOS, constantes=CONSTANTES)
