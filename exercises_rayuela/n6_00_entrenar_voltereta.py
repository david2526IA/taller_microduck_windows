"""CONFIGURA TU ENTRENAMIENTO · LA VOLTERETA: lo que se hace ANTES de pulsar "entrenar" (y como llevartelo a casa).

Ya has VISTO cuatro cosas de esta voltereta (n3_07, n3_08): como se ve un robot que no sabe nada, como aparece la habilidad, como se vuelve
irregular y como se estabiliza. Ahora vas a configurar TU entrenamiento de la misma voltereta, como si fueras a lanzarlo:

   1. elegir la TAREA            (aqui: Mjlab-Roulade-Flat-MicroDuck)
   2. leer la RECOMPENSA real    (se imprime sola: los terminos y pesos del fichero oficial, con su significado)
   3. cambiar lo que quieras     (pesos, rondas, robots a la vez, tasa de aprendizaje...)
   4. generar tu PAQUETE         (scripts listos para lanzar en un PC con GPU, o en una GPU de la nube) en mi_entrenamiento/voltereta/

Que NO se hace aqui: entrenar de verdad con mjlab. Hace falta una GPU NVIDIA y Linux (o WSL2); este PC no la tiene. Todo lo anterior al boton SI.
Lo que si puedes entrenar de verdad, en CPU, es la version pequena del taller (patada, n3_05).

COMO USARLO: ejecuta (F5) SIN tocar nada y lee la salida entera. Despues cambia UN valor, guarda (Ctrl+S) y ejecuta otra vez:
veras cambiar el comando y los scripts. No hace falta saber programar: solo cambiar numeros.
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================
# Los valores por defecto son los del entrenamiento REAL de esta voltereta (parametros guardados de esa carrera).

# ---------- 1. CUANTA EXPERIENCIA ----------
# Robots (simulaciones) que entrenan A LA VEZ en la GPU. El entrenamiento real uso 2048.
#   AFECTA A: la experiencia por minuto y la memoria de la GPU. Si no cabe, baja a 1024. MEDIDO en otra tarea (levantarse, 100 rondas):
#   con 256 robots la recompensa final fue 6,1 frente a 25,4 con 4096: pocos robots = mucho mas lento.
NUM_ENVS = 2048

# Rondas de entrenamiento (cada ronda = probar, puntuar y ajustar con miles de pasos de simulacion).
#   AFECTA A: cuanto aprende. En el entrenamiento real la voltereta APARECIO hacia la ronda 750 (lo viste en n3_07) y se estabilizo
#   hacia la 11.000; las 20.750 totales sirvieron para pulirla. Para ver que aparece basta con ~1.000.
ITERACIONES = 2000

# Cada cuantas rondas se guarda el cerebro (los checkpoints, como en n3_07). El real guardo cada 250.
#   AFECTA A: cuantas "fotos" del aprendizaje tendras para elegir. Recuerda lo de n3_08: el ultimo no siempre es el mejor.
GUARDAR_CADA = 250

# ---------- 2. EL ALGORITMO PPO ----------
# Tamano de cada ajuste del cerebro. El real uso 0.001. None = el de la tarea.
#   MEDIDO en entrenar/experimentos.sh (tarea de levantarse, 100 rondas, recompensa final): base 25,4 | con 0.00005 -> 8,8 (casi no aprende) |
#   con 0.01 -> se descontrola (recompensa de -4 mil millones).
LEARNING_RATE = 0.001

# Premio por seguir explorando (probar cosas nuevas). El real uso 0.01.
#   MEDIDO en esos mismos experimentos: con 0.1 la recompensa final fue -108 (explora tanto que no aprende).
ENTROPIA = 0.01

# Cuanto "piensa" en el futuro (0.8 = miope, 0.99 = largo plazo). El real uso 0.99.
#   MEDIDO: gamma 0.8 dio 27,3 frente a 25,4 de la base en la tarea de levantarse: ahi apenas importo.
GAMMA = 0.99

# ---------- 3. LA RECOMPENSA (lo que el robot "quiere") ----------
# Se imprimen al ejecutar los 19 terminos con su peso y su significado. Aqui eliges cuales cambiar:
#   {"termino": valor}        FIJA el peso
#   {"termino": ("*", 0.5)}   lo MULTIPLICA (0.5 = la mitad, 2 = el doble)
#
# Ideas, con una pregunta para PREDECIR antes de cambiar (y comprobarlo cuando tengas una GPU):
#   · roulade_overspeed -> 0 : sin castigo por girar rapido. El propio fichero cuenta que el PRIMER entrenamiento, sin ese coste,
#     aprendio un "latigazo" violento: la misma vuelta, mas rapido y sin cuidado. ¿Por que es "optima" para el robot, aunque sea fea?
#   · roulade_stand_tax -> 0 : sin castigo por quedarse agachado tras la vuelta. ¿Se levantara o se quedara hecho un ovillo?
#   · roulade_progress ("*", 0.5): la mitad de premio por girar. ¿Seguira intentandolo?
#   Ejemplo:  PESOS = {"roulade_overspeed": 0.0}
#   (Los terminos action_rate_l2, arrival_damping, joint_torque_rate_l2 y gentle_landing los sube un CURRICULO por etapas:
#    el valor que pongas solo vale al principio.)
PESOS = {}

# Nombre del experimento (carpeta donde se guardaran las curvas y los cerebros).
NOMBRE = "taller_voltereta"

# ====================================================================

if __name__ == "__main__":
    import entrenamiento
    entrenamiento.principal("voltereta", num_envs=NUM_ENVS, iteraciones=ITERACIONES, guardar_cada=GUARDAR_CADA, nombre=NOMBRE,
                            learning_rate=LEARNING_RATE, entropia=ENTROPIA, gamma=GAMMA, pesos=PESOS)
