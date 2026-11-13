"""CONFIGURA TU ENTRENAMIENTO · CASO 4 · EL CIRCUITO DE OBSTACULOS (estilo GTC Berlin): andar en terreno irregular.

Otro MUNDO para el mismo robot: terreno con rampas, escalones, baldosas irregulares y escombros que se hace mas dificil a medida que el
robot mejora (CURRICULO DE TERRENO). Es la receta de NVIDIA/Pollen: entrenar con miles de robots en terreno variado para que el
robot real aguante lo que se encuentre. Aqui lees la configuracion real, cambias lo que quieras y generas tu paquete en mi_entrenamiento/obstaculos/.
En CPU puedes ver y medir politicas ya entrenadas en el circuito en crescendo: n4_05_obstaculos.py y n4_06_validar_politicas.py.

COMO USARLO: ejecuta (F5) sin tocar nada y lee la salida; despues cambia UN valor y vuelve a ejecutar.
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# ---------- 1. CUANTA EXPERIENCIA ----------
NUM_ENVS = 4096      # AFECTA A: experiencia por minuto y memoria de GPU (si no cabe: 2048 o 1024).
# Rondas. Segun su ficha, rough_walk_g (el mas firme en escalones y rampas) se entreno 3.300 rondas DESDE CERO en terreno irregular;
# rough_walk_e, 800 rondas afinando alpha_walking. Tiempo: el README oficial dice ~1-2 h a 4.096 robots para un buen andar en llano.
ITERACIONES = 3300
GUARDAR_CADA = 250

# ---------- 2. EL ALGORITMO PPO (None = el de la tarea) ----------
LEARNING_RATE = None
ENTROPIA = None
GAMMA = None

# ---------- 3. LA RECOMPENSA ----------
# {"termino": valor} FIJA el peso | {"termino": ("*", 0.5)} lo MULTIPLICA. Los terminos se listan al ejecutar.
#   AFECTA A: como camina. Ideas para predecir antes de cambiar:
#     · foot_slip: castiga resbalar el pie. Mas castigo = pasos mas seguros en escalones, pero ¿mas lentos?
#     · air_time: premia levantar los pies. Menos premio = pasos mas bajos (¿tropieza mas con los escalones?)
#   Ejemplo:  PESOS = {"foot_slip": ("*", 2.0)}
PESOS = {}

# Constantes de la tarea (se listan al ejecutar): sobre todo la ALEATORIZACION de dominio y el reparto de ordenes.
#   AFECTA A: lo robusta que sera al pasar al robot real, y lo que tarda en aprender.
#   Ejemplo:  CONSTANTES = {"TURN_IN_PLACE_FRACTION": 0.3}   (mas robots mandados a girar sobre si mismos)
CONSTANTES = {}

NOMBRE = "taller_obstaculos"

# ====================================================================

if __name__ == "__main__":
    import entrenamiento
    entrenamiento.principal("obstaculos", num_envs=NUM_ENVS, iteraciones=ITERACIONES, guardar_cada=GUARDAR_CADA, nombre=NOMBRE,
                            learning_rate=LEARNING_RATE, entropia=ENTROPIA, gamma=GAMMA, pesos=PESOS, constantes=CONSTANTES)
