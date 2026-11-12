"""NIVEL 1-2 - CREA TU PROPIA ESCENA (el mundo del robot).

En MuJoCo, un mundo se DESCRIBE con piezas: suelo, cajas, luz, cuerpos con masa... y un robot dentro.
Aqui el Microduck juega a la rayuela en un mundo que TU modificas con los parametros de abajo, sin tocar los XML.
(Los XML oficiales son robot/ y rayuela-oficial/src/mjlab_microduck/robot/microduck/: ábrelos y busca estas cosas.)

COMO USARLO: cambia UN valor, guarda (Ctrl+S), CIERRA la ventana del robot y ejecuta otra vez (F5).
Controles en la TERMINAL: flechas = andar, 1-9 = patada a casilla, k/l = patada, h = a casa, n = reiniciar, q = salir.
Empuja con Ctrl + clic derecho sobre el robot.
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS DEL MUNDO ============================

# Gravedad (m/s^2). 9.81 = Tierra | 3.7 = Marte | 1.62 = Luna | 24.8 = Jupiter.
#   AFECTA A: todo. En la Luna la pelota vuela y el pato rebota; en Jupiter casi no puede levantarse.
#   OJO: el cerebro se entreno en la Tierra. Fuera de ella ve un mundo que no conoce... y se nota.
GRAVEDAD = 9.81

# Rozamiento del SUELO con las cosas (1.0 = normal | 0.1 = hielo | 2.0 = goma).
#   AFECTA A: lo que patinan los pies del pato y lo que rueda la pelota.
ROZAMIENTO_SUELO = 1.0

# Cuanto pesa el pato en total se escala con este numero (1.0 = normal, 2.0 = el doble).
#   AFECTA A: el esfuerzo que piden los motores. Un pato mas pesado se cansa: prueba 1.5.
ESCALA_MASA_PATO = 1.0

# Tamaño de la pelota (radio en metros; 0.035 = normal) y su masa en kg.
#   AFECTA A: una pelota mas grande se golpea peor; una mas pesada llega menos lejos.
RADIO_PELOTA = 0.035
MASA_PELOTA = None        # None = la del modelo

# Obstaculos: cajas que anades al mundo. Cada una: (x, y, ancho, largo, alto) en metros.
#   El pato empieza en (0,0) mirando hacia +x; la rayuela va de x=0.3 a x=2.1.
#   AFECTA A: la pelota rebota en ellas y el pato las tiene que rodear. Ejemplo: [(1.0, 0.0, 0.05, 0.15, 0.08)]
OBSTACULOS = []

# Color del suelo del tablero: (rojo, verde, azul), de 0 a 1.
#   AFECTA A: solo a lo que ves... y a lo que "ve" la camara de la vision. Prueba un tablero oscuro (0.1, 0.1, 0.1):
#   ¿sigue la vision detectando bien la pelota?
COLOR_TABLERO = (0.93, 0.93, 0.90)

# ¿Quieres que la partida lleve marcador? Un numero de casilla (1-9), "aleatorio", o None para jugar libre.
OBJETIVO = None

# ==============================================================================


def editar_escena(spec):
    """Aqui se edita el mundo ANTES de crearlo. Mira como: cada linea cambia una pieza del XML."""
    import mujoco
    spec.option.gravity = [0, 0, -GRAVEDAD]                                      # <option gravity=...>
    for g in spec.geoms:
        if g.name == "floor":
            g.friction[0] = ROZAMIENTO_SUELO                                      # <geom name="floor" friction=...>
        if g.name == "board_plate":
            g.rgba = [*COLOR_TABLERO, 1]                                          # color del tablero
        if g.name == "ball_geom":
            g.size[0] = RADIO_PELOTA                                              # radio de la pelota
            if MASA_PELOTA is not None:
                g.mass = MASA_PELOTA
    for b in spec.bodies:
        if b.name == "trunk_base" and ESCALA_MASA_PATO != 1.0:                    # el tronco lleva casi toda la masa
            b.mass *= ESCALA_MASA_PATO
    for i, (x, y, ancho, largo, alto) in enumerate(OBSTACULOS):                   # tus cajas
        spec.worldbody.add_geom(name=f"obstaculo_{i}", type=mujoco.mjtGeom.mjGEOM_BOX,
                                size=[ancho / 2, largo / 2, alto / 2], pos=[x, y, alto / 2],
                                rgba=[0.8, 0.3, 0.2, 1])


if __name__ == "__main__":
    import casos
    prueba = "--prueba" in sys.argv
    casos.lanzar("rayuela", visor=not prueba, editar_escena=editar_escena, objetivo=OBJETIVO,
                 segundos=8 if prueba else None)
