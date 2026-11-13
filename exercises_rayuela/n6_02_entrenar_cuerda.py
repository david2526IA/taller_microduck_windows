"""CONFIGURA TU ENTRENAMIENTO · CASO 2 · EL DUELO DE LA CUERDA: dos robots que aprenden jugando entre si.

Otra VERSION del mismo problema: ahora no hay un entorno fijo al que ganar, el rival tambien aprende (AUTOJUEGO). Un solo cerebro
juega los dos lados; el rival es una copia suya que se refresca cada N rondas. Se parte del cerebro de andar ya entrenado,
porque aprender a andar Y a luchar desde cero seria demasiado.

Aqui configuras ese entrenamiento (el perfil de recompensas es el del duelo real, proyecto patos_cuerda, que dio duelo2.onnx) y generas
tu paquete en mi_entrenamiento/cuerda/. En CPU puedes VER el resultado y cambiar fuerza y masa de cada pato: n4_03_cuerda.py.

ATENCION (honestidad): este caso depende de los PARCHES del proyecto patos_cuerda (reglas del duelo, victoria por cruce de linea,
refresco del rival) sobre la rama tug-etapas de microduck_rl. El paquete los menciona pero no los incluye.
COMO USARLO: ejecuta (F5) sin tocar nada y lee la salida; despues cambia UN valor y vuelve a ejecutar.
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# ---------- 1. CUANTA EXPERIENCIA ----------
# Robots (parejas de patos) a la vez. El duelo real uso 2048 (si no cabe en la GPU, 1024).
NUM_ENVS = 2048
# Rondas. El duelo real: 6.000 rondas desde el cerebro de andar (la politica publicada es de la ronda 6027).
ITERACIONES = 6000
GUARDAR_CADA = 250

# ---------- 2. EL ALGORITMO PPO ----------
# El duelo real uso learning-rate 0.0003 y entropia 0.001. None = el de la tarea.
LEARNING_RATE = 0.0003
ENTROPIA = 0.001
GAMMA = None

# ---------- 3. LA RECOMPENSA DEL DUELO ----------
# {"termino": valor} FIJA el peso | {"termino": ("*", 0.5)} lo MULTIPLICA. Se listan al ejecutar con su significado.
#   AFECTA A: el caracter del duelo. Mucho competitive_terminal = solo importa ganar; mucho rope_taut = se obsesiona con tensar la cuerda.
#   Pregunta: si fall_any = 0 (caerse no cuesta nada), ¿se lanzaran a tirar sin cuidado? ¿Y con timeout_stalemate = 0, empataran?
PESOS = {}

# ---------- 4. EL AUTOJUEGO ----------
# Cada cuantas rondas se refresca la copia que hace de rival. Pocas = rival que cambia rapido (inestable); muchas = rival "viejo".
REFRESCO_RIVAL = 10
# Lo cerca de la linea de victoria que empiezan (en metros desde su posicion normal). Mas cerca = el duelo se decide antes
# (es un "currículo inverso": empezar cerca de la victoria facilita descubrirla).
OFFSET_INICIAL = 0.45

NOMBRE = "taller_cuerda"

# ====================================================================

if __name__ == "__main__":
    import entrenamiento
    entrenamiento.principal("cuerda", num_envs=NUM_ENVS, iteraciones=ITERACIONES, guardar_cada=GUARDAR_CADA, nombre=NOMBRE,
                            learning_rate=LEARNING_RATE, entropia=ENTROPIA, gamma=GAMMA, pesos=PESOS,
                            variables_entorno={"MICRODUCK_OPPONENT_INTERVAL": REFRESCO_RIVAL, "MICRODUCK_SPAWN_OFFSET": OFFSET_INICIAL})
