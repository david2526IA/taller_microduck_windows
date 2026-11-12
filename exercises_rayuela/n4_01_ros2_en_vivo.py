"""NIVEL 4 - ROS 2 EN VIVO: nodos y topics (como en un robot de verdad).

Un sistema ROS 2 es un grupo de NODOS (programas pequeños) que hablan por TOPICS (canales con nombre):
   quien PUBLICA pone un mensaje en un topic; quien esta SUSCRITO lo recibe.  Nadie llama a nadie directamente.

En la Rayuela hay cinco nodos oficiales:
   teleop_keyboard ... publica  /rayuela/cmd_vel y /rayuela/behavior_cmd   (tu teclado)
   bridge .......... publica  /rayuela/duck_pose, /rayuela/current_policy y la imagen de la camara (la simulacion)
   vision .......... lee la imagen, publica /rayuela/target_casilla         (donde cayo la pelota)
   control ......... lee la casilla y la pose, publica cmd_vel/behavior_cmd (lleva al pato alli)
   monitor ......... solo ESCUCHA y te cuenta cuantos mensajes pasan por cada topic (como 'ros2 topic hz')

Pulsa teclas en la TERMINAL (5 = patada a casilla 5, flechas, h = a casa, n = nueva partida) y mira la tabla que se
repite cada pocos segundos: ¿que topics se mueven cuando pateas? ¿y cuando andas?

EXPERIMENTOS (cambia UN valor de abajo, guarda, cierra la ventana y lanza otra vez):
   VISION = False  -> sin el nodo de vision nadie dice donde cayo la pelota: /rayuela/target_casilla se queda en 0 mensajes.
   CONTROL = False -> el pato no va solo a la casilla: lo conduces tu. ¿Que topic deja de moverse?
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================
VISION = True        # AFECTA A: si el nodo de vision se ejecuta (detecta la pelota con la camara).
CONTROL = True       # AFECTA A: si el nodo de control se ejecuta (lleva al pato a la casilla).
VER_VISION = False   # AFECTA A: abre una ventana con lo que ve la camara enderezado (el nodo de vision la dibuja).
# ====================================================================

if __name__ == "__main__":
    import casos
    prueba = "--prueba" in sys.argv
    casos.lanzar("rayuela", visor=not prueba, vision=VISION, control=CONTROL, ver_vision=VER_VISION, monitor=True,
                 segundos=8 if prueba else None)
