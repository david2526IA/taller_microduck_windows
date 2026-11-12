"""CASO DE USO 3 - EL DUELO DE LA CUERDA (tug of war) con una politica ENTRENADA.

Dos Microducks atados por una cuerda, cada uno mirando hacia fuera. Gana quien consigue que el otro cruce SU linea
(azul a la izquierda, roja a la derecha) o se caiga; si a los 20 s nadie gana, empate. Es el proyecto patos_cuerda de
Bravo Robots: un mismo cerebro juega los dos lados (autojuego) y se entreno con mjlab y PPO en una GPU, durante mas de
6000 iteraciones, con una recompensa competitiva (ganar, tirar de la cuerda tensa, no caerse...).
Aqui solo se EJECUTA, en tu CPU, con la fisica de MuJoCo y los motores BAM.

Es el ejemplo de como se monta un entorno de DOS robots y de que cambia cuando la recompensa es competitiva.

CONTROLES (en la TERMINAL, no en la ventana del robot):
   w / s = el pato A tira mas / menos       i / k = el pato B tira mas / menos      n = nuevo combate      q = salir
   Ctrl + clic derecho sobre un pato = empujarlo

EXPERIMENTOS: cambia UN valor, guarda (Ctrl+S), CIERRA la ventana y lanza otra vez (F5).
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Cuanto "quiere" tirar cada pato: la orden de avance que recibe su cerebro (0 a 1 m/s). Con 0 se queda de pie sin tirar.
#   AFECTA A: la fuerza del tiron. Prueba A = 1.0 y B = 0.3: ¿gana siempre A? ¿O el cerebro entrenado sabe aguantar?
AVANCE_A = 0.6
AVANCE_B = 0.6

# Escala de las ordenes a los motores de B (1.0 = igual | 0.6 = un 40 % mas flojo).
#   AFECTA A: un pato con motores mas debiles. Es el "curriculo de fuerza" del entrenamiento: se entrena contra rivales mas flojos y se sube.
FUERZA_B = 1.0

# Masa del tronco de cada pato (1.0 = normal | 2.0 = el doble de pesado).
#   AFECTA A: un pato pesado cuesta mas arrastrar... pero tambien le cuesta mas mantenerse de pie.
MASA_A = 1.0
MASA_B = 1.0

# Agarre de los pies al suelo (1.0 = normal | 0.3 = casi hielo).
#   AFECTA A: en el hielo los dos patinan y casi no pueden tirar. El cerebro se entreno con rozamiento aleatorio entre 0,7 y 1,3.
ROZAMIENTO_SUELO = 1.0

# Longitud maxima de la cuerda (m). Los patos empiezan a 0,9 m uno del otro.
#   AFECTA A: con 1.0 empiezan casi tensos; con 1.6 hay holgura y el primer tiron es un golpe seco.
LARGO_CUERDA = 1.0

# Cuanto se acerca cada pato al centro al empezar (m). 0 = como en el entrenamiento.
#   AFECTA A: con 0.15 los patos empiezan mas cerca de la linea del rival: combates mas rapidos.
DESPLAZAMIENTO = 0.0

# Azar al empezar (m). 0 = siempre el mismo combate... y gana siempre el mismo: el duelo es simetrico, el ruido decide.
#   AFECTA A: la variedad entre combates. En el entrenamiento habia ruido y empujones aleatorios por todas partes.
RUIDO_INICIAL = 0.03

# ¿Que pasa si B no esta entrenado para el duelo? True = B usa el cerebro de ANDAR y se le pide avanzar.
#   AFECTA A: mide cuanto aporta entrenar con una recompensa competitiva frente a solo saber andar.
B_SOLO_ANDA = False

# Segundos de combate antes de dar empate.
TIEMPO_MAX = 20.0

# ====================================================================

if __name__ == "__main__":
    import duelo
    prueba = "--prueba" in sys.argv
    duelo.lanzar_duelo(AVANCE_A, AVANCE_B, TIEMPO_MAX, FUERZA_B, MASA_A, MASA_B, ROZAMIENTO_SUELO, LARGO_CUERDA,
                       DESPLAZAMIENTO, b_solo_anda=B_SOLO_ANDA, ruido_inicial=RUIDO_INICIAL,
                       visor=not prueba, segundos=10 if prueba else None, verbose=prueba)
