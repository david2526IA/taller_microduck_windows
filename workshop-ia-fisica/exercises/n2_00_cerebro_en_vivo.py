"""NIVEL 2 - El CEREBRO del pato, por dentro y en vivo.
Una red neuronal es una FUNCION: le entran 61 numeros (lo que siente el robot) y le salen 14
(la orden para cada uno de sus 14 motores). Lo hace 50 veces por segundo. Aqui lo ves mientras el pato anda.

Controles (pulsalos en la TERMINAL, no en el visor): Flechas = velocidad | A / E = girar | Q = salir
Ctrl + clic derecho arrastrando sobre el robot = EMPUJARLO

PRUEBAS (cambia una constante, guarda y vuelve a lanzar):
  QUITAR_SENTIDO  ¿que pasa si le quitas un sentido? Asi descubres a cuales hace caso de verdad.
  RUIDO_SENTIDOS  sentidos "borrosos": le sumamos ruido a lo que siente.
  RUIDO_ORDENES   motores "temblorosos": le sumamos ruido a lo que decide.
"""
import os, pathlib, sys
import numpy as np
import onnxruntime as ort
import mujoco

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from panel_en_vivo import Panel, SinRuido, barra, cargar_demo, nombre_motor, spark

# --- PRUEBAS: None / 0 = sin tocar ---
QUITAR_SENTIDO = None   # prueba "inclinacion", "giro", "posicion", "velocidad" o "ultima_orden"
RUIDO_SENTIDOS = 0.0    # prueba 0.05, 0.2, 0.5
RUIDO_ORDENES = 0.0     # prueba 0.1, 0.3, 0.6

# Las 61 entradas, por grupos: nombre -> (desde, hasta, escala para dibujar)
SENTIDOS = {
    "giro":        (0, 3, 2.0),     # giro del cuerpo (rad/s)
    "inclinacion": (3, 6, 1.0),     # hacia donde cae la gravedad respecto al tronco
    "posicion":    (6, 20, 0.4),    # angulo de cada motor (rad)
    "velocidad":   (20, 34, 4.0),   # velocidad de cada motor (rad/s)
    "ultima_orden": (34, 48, 0.8),  # lo que ordeno hace un instante
    "pedido":      (48, 61, 1.0),   # la orden que le damos con las flechas
}
ETIQUETAS = {"giro": "giro del cuerpo", "inclinacion": "inclinacion", "posicion": "posicion motores",
             "velocidad": "velocidad motores", "ultima_orden": "ultima orden", "pedido": "orden (flechas)"}
if QUITAR_SENTIDO is not None and QUITAR_SENTIDO not in SENTIDOS:
    raise SystemExit(f"QUITAR_SENTIDO debe ser None o uno de: {', '.join(SENTIDOS)}")

demo = cargar_demo()
rng = np.random.default_rng(0)
panel = Panel()
estado = dict(obs=np.zeros(61), accion=np.zeros(14), cerebro="", llamadas=0, t=0.0, modelo=None)


class SesionEspia(ort.InferenceSession):
    """Una sesion de onnxruntime que apunta lo que entra y lo que sale del cerebro (y, si queremos, lo estropea)."""

    def __init__(self, ruta, *args, **kwargs):
        super().__init__(ruta, *args, **kwargs)
        self.ruta = str(ruta)

    def run(self, salidas, entradas, *args, **kwargs):
        nombre = next(iter(entradas))
        obs = np.array(entradas[nombre], dtype=np.float32)
        if obs.shape[-1] == 61:
            if QUITAR_SENTIDO:
                desde, hasta, _ = SENTIDOS[QUITAR_SENTIDO]
                obs[..., desde:hasta] = 0.0
            if RUIDO_SENTIDOS:
                obs = obs + rng.normal(0, RUIDO_SENTIDOS, obs.shape).astype(np.float32)
            resultado = super().run(salidas, {nombre: obs}, *args, **kwargs)
            accion = np.array(resultado[0], dtype=np.float32)
            if RUIDO_ORDENES:
                accion = accion + rng.normal(0, RUIDO_ORDENES, accion.shape).astype(np.float32)
            estado.update(obs=obs.reshape(-1), accion=accion.reshape(-1), cerebro=self.ruta.split("/")[-1].split("\\")[-1])
            estado["llamadas"] += 1
            if estado["llamadas"] % 10 == 0:
                dibujar()
            return [accion] + list(resultado[1:])
        return super().run(salidas, entradas, *args, **kwargs)


def dibujar():
    obs, accion = estado["obs"], estado["accion"]
    lineas = ["CEREBRO EN VIVO · entran 61 números → salen 14 órdenes · 50 veces por segundo",
              f"cerebro activo: {estado['cerebro']}   |   sentido quitado: {QUITAR_SENTIDO or 'ninguno'}"
              f"   |   ruido sentidos: {RUIDO_SENTIDOS}   ruido órdenes: {RUIDO_ORDENES}", "",
              "ENTRADAS (lo que siente)"]
    for clave, (desde, hasta, escala) in SENTIDOS.items():
        quitado = "   <- QUITADO" if clave == QUITAR_SENTIDO else ""
        if clave == "pedido":
            dato = f"adelante {obs[48]:+.2f} · lado {obs[49]:+.2f} · giro {obs[50]:+.2f}"
        else:
            dato = f"{spark(obs[desde:hasta], escala):<14} ({hasta - desde})"
        lineas.append(f"  {ETIQUETAS[clave]:<18}{dato}{quitado}")
    lineas += ["", "SALIDAS (la orden a cada motor)   -0.8 ◄── 0 ──► +0.8"]
    modelo = estado["modelo"]
    for i, valor in enumerate(accion):
        nombre = nombre_motor(mujoco.mj_id2name(modelo, mujoco.mjtObj.mjOBJ_ACTUATOR, i)) if modelo else f"motor {i}"
        lineas.append(f"  {nombre:<22}{barra(valor, 0.8)}  {valor:+.2f}")
    lineas += ["", "Prueba: empuja al pato con Ctrl + clic derecho y mira qué órdenes cambian. Q para salir."]
    panel.mostrar(lineas, estado["llamadas"] / 50)


paso_real = mujoco.mj_step


def mj_step_con_nombres(modelo, datos, *args, **kwargs):
    estado["modelo"] = modelo
    return paso_real(modelo, datos, *args, **kwargs)


ort.InferenceSession = SesionEspia
mujoco.mj_step = mj_step_con_nombres
sys.stdout = SinRuido(sys.stdout)
demo.main()
sys.stdout.flush()
os._exit(0)  # evita un 'segmentation fault' de GLFW al cerrar el visor
