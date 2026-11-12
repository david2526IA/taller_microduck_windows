"""NIVEL 2 - La RECOMPENSA del pato, en vivo.
Para entrenar un robot, en cada paso se le pone una nota: la RECOMPENSA. Es una suma de piezas,
cada una multiplicada por su PESO. Aqui ves esa nota mientras manejas al pato y lo empujas.

Controles (pulsalos en la TERMINAL, no en el visor): Flechas = velocidad | A / E = girar | Q = salir
Ctrl + clic derecho arrastrando sobre el robot = EMPUJARLO

PRUEBAS (cambia un peso, guarda y vuelve a lanzar):
  1) Normal: anda y empuja al pato. ¿Que piezas bajan cuando casi se cae?
  2) PESO_AVANZAR = 5 y los demas pesos en 0: solo premiamos avanzar. ¿Que pasa con la nota cuando
     el pato se tira hacia delante y se cae? Un robot que solo viera esa nota aprenderia a tirarse.
  3) PESO_ESFUERZO = -1: castigamos gastar energia. ¿Que pasa con el total mientras anda?
"""
import os, pathlib, sys
from collections import deque
import numpy as np
import mujoco

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from panel_en_vivo import Panel, SinRuido, barra_positiva, cargar_demo

# --- LOS PESOS (lo que le importa al entrenador) ---
PESO_ALTURA = 1.0      # tener el tronco a la altura de pie
PESO_VERTICAL = 1.5    # estar bien vertical (en el entrenamiento real de StandUp tambien es 1.5)
PESO_AVANZAR = 1.0     # moverse hacia delante
PESO_ESFUERZO = -0.1   # castigo por gastar energia en los motores (en el real, action_rate vale -0.1)

ALTURA_DE_PIE = 0.12   # m, tronco del pato de pie
ALTURA_CAIDA = 0.07    # por debajo, se ha caido
VELOCIDAD_MAX = 0.3    # m/s: con esta velocidad se lleva toda la nota de "avanzar"
ESFUERZO_MAX = 0.1     # esfuerzo medio de los motores que se considera "mucho" (andando normal: ~0.06)

demo = cargar_demo()
panel = Panel()
piezas = ("altura", "vertical", "avanzar", "esfuerzo")
pesos = dict(altura=PESO_ALTURA, vertical=PESO_VERTICAL, avanzar=PESO_AVANZAR, esfuerzo=PESO_ESFUERZO)
etiquetas = dict(altura="altura del tronco", vertical="verticalidad", avanzar="avanzar", esfuerzo="esfuerzo motores")
suma = dict.fromkeys(piezas, 0.0)
cuenta = [0]
estado = dict(tronco=None, acumulado=0.0, pasos=0, caido=False, ultimo_panel=0.0)
reciente = deque(maxlen=500)           # las notas de los ultimos 10 s (a 50 pasos por segundo)
paso_real = mujoco.mj_step


def valores_de_las_piezas(modelo, datos):
    """Cada pieza vale entre 0 (mal) y 1 (perfecto)."""
    if estado["tronco"] is None:
        estado["tronco"] = mujoco.mj_name2id(modelo, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
    i = estado["tronco"]
    giro = datos.xmat[i].reshape(3, 3)                     # como esta girado el tronco
    inclinacion = np.arccos(np.clip(giro[2, 2], -1.0, 1.0))  # 0 = vertical
    adelante = float(giro[:, 0] @ datos.qvel[0:3])           # velocidad hacia donde mira el tronco
    esfuerzo = float(np.mean(np.abs(datos.ctrl)))
    return dict(
        altura=float(np.exp(-(((datos.qpos[2] - ALTURA_DE_PIE) / 0.03) ** 2))),
        vertical=float(np.exp(-((inclinacion / 0.105) ** 2))),          # margen de unos 6 grados
        avanzar=float(np.clip(adelante / VELOCIDAD_MAX, 0.0, 1.0)),
        esfuerzo=float(np.clip(esfuerzo / ESFUERZO_MAX, 0.0, 1.0)),
    )


def mj_step_con_recompensa(modelo, datos, *args, **kwargs):
    paso_real(modelo, datos, *args, **kwargs)
    v = valores_de_las_piezas(modelo, datos)
    for p in piezas:
        suma[p] += v[p]
    cuenta[0] += 1
    estado["caido"] = bool(datos.qpos[2] < ALTURA_CAIDA)
    if cuenta[0] % 4 == 0:                              # un paso de politica = 4 pasos de fisica (50 Hz)
        nota = sum(pesos[p] * v[p] for p in piezas)
        reciente.append(nota)
        estado["acumulado"] += nota
        estado["pasos"] += 1
    if datos.time - estado["ultimo_panel"] >= 0.2:       # refresco 5 veces por segundo
        estado["ultimo_panel"] = datos.time
        dibujar(datos.time)


def dibujar(t):
    n = max(cuenta[0], 1)
    medias = {p: suma[p] / n for p in piezas}
    suma.update(dict.fromkeys(piezas, 0.0))
    cuenta[0] = 0
    maximo = sum(w for w in pesos.values() if w > 0)
    lineas = ["RECOMPENSA EN VIVO · en cada paso, la nota es una suma de piezas × pesos",
              "(los pesos se cambian en el fichero: PESO_ALTURA, PESO_VERTICAL, PESO_AVANZAR, PESO_ESFUERZO)", "",
              f"  {'pieza':<18}{'valor (0 a 1)':<24}{'peso':>6}{'aporte':>9}"]
    total = 0.0
    for p in piezas:
        aporte = pesos[p] * medias[p]
        total += aporte
        lineas.append(f"  {etiquetas[p]:<18}{barra_positiva(medias[p], 20):<24}{pesos[p]:>+6.1f}{aporte:>+9.2f}")
    media10 = sum(reciente) / len(reciente) if reciente else 0.0
    lineas += ["  " + "-" * 56, f"  {'NOTA AHORA':<18}{barra_positiva(max(total, 0) / maximo if maximo else 0, 20):<24}{'':>6}{total:>+9.2f}"
               f"   (máximo {maximo:.1f})",
               "", f"  media de los últimos 10 s: {media10:+.2f}      puntos acumulados: {estado['acumulado']:+.0f}",
               "  " + ("*** SE HA CAÍDO ***" if estado["caido"] else "De pie."),
               "", "Empuja al pato con Ctrl + clic derecho y mira qué piezas bajan. Q para salir."]
    panel.mostrar(lineas, t)


mujoco.mj_step = mj_step_con_recompensa
sys.stdout = SinRuido(sys.stdout)
demo.main()
sys.stdout.flush()
os._exit(0)  # evita un 'segmentation fault' de GLFW al cerrar el visor
