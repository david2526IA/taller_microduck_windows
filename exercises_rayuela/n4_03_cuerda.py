"""CASO DE USO 3 - LA CUERDA (tug of war): dos Microducks tirando cada uno de un extremo.

Esto muestra COMO SE MONTA un entorno con DOS robots en MuJoCo: dos cuerpos con su nombre propio (duck0_, duck1_),
un "tendon" que hace de cuerda entre los dos, y un cerebro por pato.
Ojo, para no engañar a nadie: el repo microduck-tug-of-war es una base EXPERIMENTAL sin cerebro entrenado para esto.
Aqui cada pato usa el cerebro de ANDAR (alpha_walking.onnx): "tirar" es pedirle que ande hacia delante, de espaldas
a la cuerda. Para un tira y afloja de verdad habria que ENTRENAR con una recompensa competitiva
(premiar arrastrar al rival, castigar caerse): justo lo que se hace en n3_05, pero con dos robots.

CONTROLES (en la TERMINAL, no en la ventana del robot):
   w / s  = el pato A (izquierda) tira mas / menos     i / k = el pato B (derecha) tira mas / menos
   espacio = los dos sueltan     n = REINICIAR (patos en su sitio)     q = salir
   Ctrl + clic derecho sobre un pato = empujarlo

EXPERIMENTOS: cambia UN valor, guarda (Ctrl+S), CIERRA la ventana y lanza otra vez (F5).
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Cuanto tira cada pato = velocidad que le pide al cerebro de andar (0 a 0.3 m/s). Con 0 el pato solo se queda de pie.
#   AFECTA A: la fuerza con la que se aleja de la cuerda. Prueba A = 0.3 y B = 0.1: ¿quien gana?
FUERZA_A = 0.15
FUERZA_B = 0.15

# Masa del tronco de cada pato (1.0 = normal | 2.0 = el doble de pesado).
#   AFECTA A: un pato pesado cuesta mas arrastrar... pero tambien le cuesta mas andar. ¿Compensa?
MASA_A = 1.0
MASA_B = 1.0

# Agarre de los pies al suelo (1.0 = normal | 0.2 = hielo | 2.0 = goma).
#   AFECTA A: en hielo los dos patinan y casi no se puede tirar; el que pesa mas deja de tener ventaja.
ROZAMIENTO_SUELO = 1.0

# Longitud maxima de la cuerda, en metros. Los patos empiezan a 0.9 m uno del otro.
#   AFECTA A: con 0.9 empiezan ya tensos; con 1.5 hay holgura y el primer tiron es un golpe seco.
LARGO_CUERDA = 1.0

# 0 = cuerda que no se estira | mayor que 0 = cuerda elastica (como una goma). Prueba 20.
#   AFECTA A: una cuerda elastica guarda energia y devuelve el tiron; mas dificil de controlar.
RIGIDEZ_CUERDA = 0.0

# ====================================================================

if __name__ == "__main__":
    import cuerda
    prueba = "--prueba" in sys.argv
    cuerda.lanzar_cuerda(FUERZA_A, FUERZA_B, MASA_A, MASA_B, ROZAMIENTO_SUELO, LARGO_CUERDA, RIGIDEZ_CUERDA,
                         visor=not prueba, segundos=6 if prueba else None)
