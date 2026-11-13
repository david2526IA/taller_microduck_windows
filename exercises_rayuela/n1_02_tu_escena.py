"""BLOQUE 1 - LABORATORIO DE MUNDOS: crea el mundo del robot y mira como cambia lo que pasa.

En MuJoCo un mundo se DESCRIBE con piezas: suelo, cielo, luz, gravedad, cajas, rampas... y un robot dentro.
Aqui el Microduck esta en la partida de la Rayuela y TU cambias el mundo con los parametros de abajo, sin tocar los XML.
Cada parametro dice en un comentario QUE cambia y QUE vas a VER. Cambia UNO cada vez.

COMO USARLO: cambia un valor -> guarda (Ctrl+S) -> CIERRA la ventana del robot -> ejecuta otra vez (F5).
Controles en la TERMINAL (no en la ventana): flechas = andar, 1-9 = patada a casilla, k/l = patada, h = a casa,
n = reiniciar, q = salir. Empuja al robot con Ctrl + clic derecho sobre el.

RETOS (de menos a mas):
  1. Pon MUNDO = "luna" y patea a la casilla 5. ¿Llega mas lejos? ¿Por que?
  2. Pon MUNDO = "hielo" y haz que el pato ande. ¿Se resbala? Prueba ROZAMIENTO_SUELO = 3.0 para arreglarlo.
  3. Pinta tu propio mundo: COLOR_SUELO_1, COLOR_SUELO_2 y COLOR_CIELO. (La vision de la camara tambien lo nota.)
  4. Pon una rampa o una caja delante del pato en OBJETOS y mira como la esquiva... o no.
  5. Construye un laberinto con cajas en OBJETOS y llega a la casilla 9 sin tirar nada.
"""
import math, pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS DEL MUNDO ============================

# ---------- 1. UN MUNDO YA HECHO (opcional) ----------
# "tierra" | "luna" | "marte" | "hielo" | "desierto" | "noche" | None.
#   AFECTA A: pone de golpe gravedad, rozamiento y colores. Despues, los parametros de abajo que NO sean None lo pisan.
MUNDO = None

# ---------- 2. LA FISICA ----------
# Gravedad (m/s^2): 9.81 Tierra | 3.7 Marte | 1.62 Luna | 24.8 Jupiter.
#   AFECTA A: todo. En la Luna la pelota vuela y el pato rebota; en Jupiter casi no puede levantarse.
#   OJO: el cerebro se entreno en la Tierra. Fuera de ella ve un mundo que no conoce... y se nota.
GRAVEDAD = None

# Rozamiento del SUELO (1.0 normal | 0.1 hielo | 2.0 goma).
#   AFECTA A: lo que resbalan los pies del pato y lo que rueda la pelota.
ROZAMIENTO_SUELO = None

# Peso total del pato multiplicado por este numero (1.0 normal | 2.0 el doble).
#   AFECTA A: el esfuerzo de los motores. Un pato pesado se cansa: prueba 1.5.
ESCALA_MASA_PATO = 1.0

# La pelota: radio en metros (0.035 normal) y masa en kg (None = la del modelo).
#   AFECTA A: una pelota grande se golpea peor; una pesada llega menos lejos con la misma patada.
RADIO_PELOTA = 0.035
MASA_PELOTA = None

# ---------- 3. LOS COLORES (rojo, verde, azul; de 0 a 1) ----------
# Los dos colores del suelo (forman el tablero de ajedrez) y los dos del cielo (arriba y abajo).
#   AFECTA A: solo a lo que ves... y a lo que "ve" la camara de vision del robot. Prueba un suelo muy oscuro:
#   ¿sigue la vision detectando bien la pelota?
COLOR_SUELO_1 = None
COLOR_SUELO_2 = None
COLOR_CIELO_ARRIBA = None
COLOR_CIELO_ABAJO = None

# Color del tablero de la rayuela.
COLOR_TABLERO = (0.93, 0.93, 0.90)

# ---------- 4. LOS OBJETOS: lo que anades al mundo ----------
# Cada objeto es un diccionario. Tipos: "caja" | "esfera" | "cilindro" | "rampa".
#   x, y     posicion en metros (el pato empieza en (0,0) mirando a +x; la rayuela va de x=0.3 a x=2.1)
#   tam      caja/rampa: (ancho, largo, alto) | esfera: (radio,) | cilindro: (radio, alto)
#   angulo   solo rampa: inclinacion en grados (se sube hacia +x)
#   color    (rojo, verde, azul)
#   fijo     True = no se mueve | False = pesa y el pato lo puede empujar
#   AFECTA A: la pelota rebota en ellos, el pato los tiene que rodear, subir o empujar.
#   EJEMPLOS (quita el # para probar):
#      dict(tipo="caja", x=1.0, y=0.0, tam=(0.05, 0.15, 0.08), color=(0.8, 0.3, 0.2), fijo=True)
#      dict(tipo="rampa", x=0.6, y=-0.25, tam=(0.2, 0.2, 0.01), angulo=8, color=(0.3, 0.6, 0.9), fijo=True)
#      dict(tipo="esfera", x=0.5, y=0.2, tam=(0.04,), color=(0.9, 0.8, 0.1), fijo=False)
OBJETOS = []

# ---------- 5. LA PARTIDA ----------
# Un numero de casilla (1-9), "aleatorio", o None para jugar libre.
#   AFECTA A: con numero, la partida lleva marcador y te dice si acertaste.
OBJETIVO = None

# ==============================================================================

MUNDOS = {      # gravedad, rozamiento, suelo_1, suelo_2, cielo_arriba, cielo_abajo
    "tierra":   (9.81, 1.0, (0.2, 0.3, 0.4), (0.1, 0.2, 0.3), (0.3, 0.5, 0.7), (0.0, 0.0, 0.0)),
    "luna":     (1.62, 1.0, (0.55, 0.55, 0.55), (0.40, 0.40, 0.40), (0.02, 0.02, 0.05), (0.0, 0.0, 0.0)),
    "marte":    (3.70, 1.2, (0.70, 0.35, 0.20), (0.55, 0.28, 0.16), (0.80, 0.55, 0.40), (0.35, 0.20, 0.15)),
    "hielo":    (9.81, 0.1, (0.75, 0.90, 0.95), (0.60, 0.80, 0.90), (0.50, 0.70, 0.90), (0.8, 0.9, 1.0)),
    "desierto": (9.81, 1.4, (0.85, 0.72, 0.45), (0.78, 0.63, 0.36), (0.55, 0.75, 0.95), (0.95, 0.85, 0.65)),
    "noche":    (9.81, 1.0, (0.08, 0.10, 0.16), (0.04, 0.05, 0.09), (0.0, 0.0, 0.05), (0.0, 0.0, 0.0)),
}


def _valor(propio, mundo, indice, por_defecto):
    """El parametro propio manda; si es None, manda el mundo elegido; si no hay mundo, el valor normal."""
    if propio is not None:
        return propio
    if MUNDO is not None:
        return MUNDOS[MUNDO][indice]
    return por_defecto


def editar_escena(spec):
    """Aqui se edita el mundo ANTES de crearlo. Mira como: cada bloque cambia una pieza del XML."""
    import mujoco
    if MUNDO is not None and MUNDO not in MUNDOS:
        raise SystemExit(f"MUNDO = {MUNDO!r} no existe. Opciones: {', '.join(MUNDOS)} o None.")
    spec.option.gravity = [0, 0, -_valor(GRAVEDAD, MUNDO, 0, 9.81)]                          # <option gravity=...>
    roz = _valor(ROZAMIENTO_SUELO, MUNDO, 1, 1.0)
    for t in spec.textures:                                                                   # colores: <texture rgb1 rgb2>
        if t.type == mujoco.mjtTexture.mjTEXTURE_SKYBOX:
            t.rgb1 = list(_valor(COLOR_CIELO_ARRIBA, MUNDO, 4, t.rgb1))
            t.rgb2 = list(_valor(COLOR_CIELO_ABAJO, MUNDO, 5, t.rgb2))
        elif t.name == "groundplane":
            t.rgb1 = list(_valor(COLOR_SUELO_1, MUNDO, 2, t.rgb1))
            t.rgb2 = list(_valor(COLOR_SUELO_2, MUNDO, 3, t.rgb2))
    for g in spec.geoms:
        if g.name in ("floor", "board_plate", "left_foot_collision", "right_foot_collision"):
            g.friction[0] = roz                                                               # <geom friction=...>: el suelo, el tablero y los pies
        if g.name == "board_plate":
            g.rgba = [*COLOR_TABLERO, 1]                                                      # color del tablero
        if g.name == "ball_geom":
            g.size[0] = RADIO_PELOTA                                                          # radio de la pelota
            g.friction[0] = 0.5 * roz                                                         # la pelota (0.5 es su valor normal)
            if MASA_PELOTA is not None:
                g.mass = MASA_PELOTA
    for b in spec.bodies:
        if b.name == "trunk_base" and ESCALA_MASA_PATO != 1.0:                                # el tronco lleva casi toda la masa
            b.mass *= ESCALA_MASA_PATO
    for i, o in enumerate(OBJETOS):                                                           # tus objetos
        _anadir_objeto(spec, i, o)


def _anadir_objeto(spec, i, o):
    import mujoco
    tipo, tam = o.get("tipo", "caja"), o.get("tam", (0.1, 0.1, 0.05))
    x, y, color = o.get("x", 1.0), o.get("y", 0.0), (*o.get("color", (0.8, 0.3, 0.2)), 1)
    fijo = o.get("fijo", True)
    cuerpo = spec.worldbody.add_body(name=f"objeto_{i}")
    if tipo in ("caja", "rampa"):
        ancho, largo, alto = tam
        ang = math.radians(o.get("angulo", 0.0)) if tipo == "rampa" else 0.0
        z = alto / 2 + (math.sin(ang) * ancho / 2 if tipo == "rampa" else 0.0)
        cuerpo.pos = [x, y, z]
        if tipo == "rampa":                                      # inclinada: sube hacia +x
            cuerpo.quat = [math.cos(-ang / 2), 0, math.sin(-ang / 2), 0]
        geo = dict(type=mujoco.mjtGeom.mjGEOM_BOX, size=[ancho / 2, largo / 2, alto / 2])
    elif tipo == "esfera":
        cuerpo.pos = [x, y, tam[0]]
        geo = dict(type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[tam[0], 0, 0])
    elif tipo == "cilindro":
        cuerpo.pos = [x, y, tam[1] / 2]
        geo = dict(type=mujoco.mjtGeom.mjGEOM_CYLINDER, size=[tam[0], tam[1] / 2, 0])
    else:
        raise SystemExit(f"Objeto {i}: tipo {tipo!r} no existe. Usa caja, esfera, cilindro o rampa.")
    if not fijo:
        cuerpo.add_freejoint()
    cuerpo.add_geom(name=f"objeto_{i}_geom", rgba=color, density=300, **geo)


if __name__ == "__main__":
    import casos
    prueba = "--prueba" in sys.argv
    casos.lanzar("rayuela", visor=not prueba, editar_escena=editar_escena, objetivo=OBJETIVO,
                 segundos=8 if prueba else None)
