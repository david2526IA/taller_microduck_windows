"""CASO DE USO 4 - EL BALANCIN: mantener el equilibrio sobre un suelo que se mueve.

El Microduck se sube a una tabla apoyada en un eje (un balancin). Si el pato cambia el peso hacia delante, la tabla
se inclina... y el pato tiene que reaccionar. Es la prueba de que un cerebro entrenado en suelo PLANO no solo anda:
tambien COMPENSA lo que no esperaba (lo mismo que hace con un empujon).
Aviso: el cerebro de equilibrio (alpha_standing.onnx) NO se entreno con balancines. Aqui ves hasta donde aguanta
sin ensayar, y con los parametros de abajo buscas donde se rompe: eso es la base de la 'aleatorizacion del dominio'
(entrenar con balancines mas o menos duros para que aguante todos).

CONTROLES (en la TERMINAL): flechas = andar sobre la tabla | espacio = parar | h = a casa
   n = REINICIAR | y = sentarse/levantarse | q = salir | Ctrl + clic derecho sobre el pato o la tabla = empujar

EXPERIMENTOS: cambia UN valor, guarda (Ctrl+S), CIERRA la ventana y lanza otra vez (F5).
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Longitud de la tabla en metros (a lo largo de x). Mas larga = mas sitio, pero la punta baja mas al inclinarse.
#   AFECTA A: cuanto se puede mover el pato antes de caerse de la tabla.
LARGO_TABLA = 0.50

# Cuanto se puede inclinar la tabla (grados a cada lado).
#   AFECTA A: el tope del balanceo. 4 = casi plana | 12 = balanceo grande. Mas inclinacion = mas dificil.
INCLINACION_MAX = 8

# Fuerza que devuelve la tabla a la horizontal (como un muelle). 0 = tabla totalmente libre.
#   AFECTA A: con 0 el pato lo tiene dificilisimo; con 5.0 la tabla es casi un suelo rigido. Prueba 3.0 (facil), 1.0, 0.3 y 0 (casi imposible).
RIGIDEZ_MUELLE = 3.0

# Freno del balanceo (amortiguacion). Mas alto = la tabla se mueve mas despacio.
#   AFECTA A: con poco freno la tabla oscila y el pato recibe tirones; con mucho, se "pega".
AMORTIGUACION = 0.3

# Peso de la tabla en kg.
#   AFECTA A: una tabla pesada se inclina menos con el pato encima y vuelve mas despacio.
MASA_TABLA = 0.2

# Agarre entre la tabla y los pies (1.0 normal | 0.2 hielo).
#   AFECTA A: en hielo los pies resbalan sobre la tabla inclinada.
ROZAMIENTO = 1.0

# Cuanto se inclina la tabla AL EMPEZAR (grados; positivo = baja la parte delantera).
#   AFECTA A: el pato empieza en un suelo ya torcido. ¿Hasta que inclinacion inicial lo aguanta?
INCLINACION_INICIAL = 0

# ====================================================================

ALTO_EJE = 0.065          # altura del centro de la tabla sobre el suelo (m)
GROSOR = 0.02             # grosor de la tabla (m)


def editar_escena(spec):
    """Construye el balancin en el mundo: una tabla con una bisagra (articulacion) y un eje que la sujeta."""
    import math, mujoco
    tabla = spec.worldbody.add_body(name="balancin", pos=[0, 0, ALTO_EJE])
    tabla.add_joint(name="balancin_bisagra", type=mujoco.mjtJoint.mjJNT_HINGE, axis=[0, 1, 0],
                    limited=True, range=[-math.radians(INCLINACION_MAX), math.radians(INCLINACION_MAX)],
                    stiffness=RIGIDEZ_MUELLE, damping=AMORTIGUACION)
    tabla.add_geom(name="balancin_tabla", type=mujoco.mjtGeom.mjGEOM_BOX, size=[LARGO_TABLA / 2, 0.15, GROSOR / 2],
                   mass=MASA_TABLA, friction=[ROZAMIENTO, 0.005, 0.0001], rgba=[0.75, 0.55, 0.3, 1])
    # el eje que la sujeta (solo se ve; no choca con nada)
    spec.worldbody.add_geom(name="balancin_eje", type=mujoco.mjtGeom.mjGEOM_CYLINDER, size=[0.02, 0.15, 0],
                            euler=[math.pi / 2, 0, 0], pos=[0, 0, ALTO_EJE - 0.03], rgba=[0.3, 0.3, 0.3, 1],
                            contype=0, conaffinity=0)


def inclinar_al_empezar(model, data):
    """Una vez creado el mundo: gira la bisagra a la inclinacion inicial pedida."""
    import math
    adr = model.jnt_qposadr[model.joint("balancin_bisagra").id]
    data.qpos[adr] = math.radians(INCLINACION_INICIAL)


if __name__ == "__main__":
    import casos
    prueba = "--prueba" in sys.argv
    casos.lanzar("rayuela", visor=not prueba, vision=False, control=False, editar_escena=editar_escena,
                 editar_modelo=inclinar_al_empezar, altura_pato=ALTO_EJE + GROSOR / 2 + 0.125,
                 segundos=15 if prueba else None)
