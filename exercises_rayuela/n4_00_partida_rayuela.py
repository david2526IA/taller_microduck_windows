"""NIVEL 4 - LA PARTIDA DE LA RAYUELA (el reto del taller).

El Microduck tiene que meter la pelota en la casilla que se le pide. Es el sistema completo:
  simulacion MuJoCo  ->  cerebro de patada (ONNX)  ->  camara y VISION  ->  CONTROL  ->  el pato camina a la casilla
Todo corre con el codigo OFICIAL de Bravo Robots (carpeta rayuela-oficial/), con ROS 2 imitado en Windows.

COMO SE JUEGA (teclas en la TERMINAL, no en la ventana del robot):
  k / l ........ patada con el pie izquierdo / derecho a la VELOCIDAD_PATADA que pongas abajo
  1 ... 9, 0 ... patada "automatica" a esa casilla (el sistema elige pie y velocidad con su tabla de calibracion)
  flechas ...... andar y girar        espacio = parar       x = parar todo
  h ............ el pato vuelve solo a casa             n = NUEVA RONDA (reinicia pato y pelota)
  r voltereta   y sentarse / levantarse      q salir     Ctrl + clic derecho sobre el robot = empujarlo

PUNTOS: aciertas la casilla = 10 | casilla vecina = 3 | otra = 0   (cambialo en PUNTOS)

ANTES DE EMPEZAR: cambia UN valor de la lista de abajo, guarda (Ctrl+S), cierra la ventana del robot y lanza otra vez.
"""
import pathlib, sys

# ====================== PARAMETROS: AQUI ES DONDE JUEGAS ======================

# Casilla que hay que acertar: un numero 1-9, o "aleatorio" (cambia en cada ronda).
#   AFECTA A: el marcador. No cambia como patea el pato, solo que cuenta como acierto.
OBJETIVO = 5

# Velocidad de salida de la pelota (m/s) al pulsar k / l. Prueba entre 0.3 y 1.8.
#   AFECTA A: lo lejos que llega la pelota. Es la "fuerza" de la patada que el cerebro aprendio a controlar.
#   PISTA: 0.34 m/s cae en la casilla 2, 0.9 m/s cae en la 8. Tu trabajo es CALIBRAR: ¿que velocidad da la casilla 5?
#   Pon None para que k / l usen la velocidad por defecto del sistema.
VELOCIDAD_PATADA = 0.9

# Tu politica de patada entrenada en n3_05 (un .json). Con ella, las teclas 1-9 patean como TU la entrenaste.
#   Si todavia no has entrenado (n3_05), no existe el fichero y se usa la tabla OFICIAL; ponlo en None para no ver el aviso.
#   AFECTA A: quien decide pie y velocidad al pulsar 1-9: la tabla OFICIAL (None) o TU cerebro. ¿Quien acierta mas?
TABLA_PROPIA = pathlib.Path(__file__).resolve().parent.parent / "mi_tabla_patada.json"

# Puntos segun el resultado: 0 = acierto, 1 = casilla vecina, 2 = cualquier otra.
#   AFECTA A: el marcador. Prueba a premiar mas el acierto exacto: {0: 20, 1: 2, 2: 0}
PUNTOS = {0: 10, 1: 3, 2: 0}

# ¿Ejecutar el nodo de VISION? Es la camara que detecta en que casilla se para la pelota.
#   AFECTA A: si no hay vision, nadie avisa de donde cayo la pelota: no hay marcador ni el pato va a la casilla.
VISION = True

# ¿Ejecutar el nodo de CONTROL? Es el que hace caminar al pato hasta la casilla donde cayo la pelota.
#   AFECTA A: con CONTROL = False el pato se queda quieto tras patear y conduces tu con las flechas.
CONTROL = True

# Abre una ventana con lo que "ve" la camara ya enderezado (tablero visto desde arriba) y la pelota detectada.
#   AFECTA A: solo a lo que ves; sirve para entender la vision.
VER_VISION = False

# ================================================================================

AQUI = pathlib.Path(__file__).resolve().parent.parent
AQUI_RAIZ = AQUI                          # la carpeta del proyecto (para TABLA_PROPIA)
sys.path.insert(0, str(AQUI / "windows"))
import casos  # noqa: E402

if __name__ == "__main__":
    prueba = "--prueba" in sys.argv          # uso interno: comprobar que arranca, sin ventana
    casos.lanzar("rayuela", visor=not prueba, vision=VISION, control=CONTROL, ver_vision=VER_VISION,
                 objetivo=OBJETIVO, puntos=PUNTOS, velocidad_patada=VELOCIDAD_PATADA, tabla_propia=TABLA_PROPIA,
                 segundos=12 if prueba else None)
