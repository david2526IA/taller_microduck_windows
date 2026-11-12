"""NIVEL 2 - DENTRO del cerebro: ve pasar los datos por la red, capa a capa, mientras el pato anda.
El cerebro del pato es un fichero (.onnx) con 197.896 numeros (los PESOS). Cada 20 ms hace una cuenta:
   61 entradas -> normalizar -> capa 1 (512 neuronas) -> capa 2 (256) -> capa 3 (128) -> 14 ordenes
Aqui hacemos esa cuenta NOSOTROS con numpy (scripts/leer_onnx.py) y la ves en directo. Es la misma que hace onnxruntime.

Controles (pulsalos en la TERMINAL, no en el visor): Flechas = velocidad | A / E = girar | Q = salir
Ctrl + clic derecho arrastrando sobre el robot = EMPUJARLO

PRUEBAS (cambia una constante, guarda, CIERRA la ventana y vuelve a lanzar):
  CEREBRO         prueba "progresion_0_recien_nacido" ... "progresion_4_mejor": la misma red, con otros pesos.
                  ¿Cambia la forma de la actividad? ¿Y cuantas neuronas estan activas?
  APAGAR_CAPA1    apaga un % de neuronas de la capa 1 (0.5 = la mitad). ¿Cuantas se pueden quitar antes de que se caiga?
                  Sorpresa: aguanta con el 95 % apagado y solo cae al apagarlas TODAS (1.0). El trabajo esta muy repartido:
                  no hay una "neurona del equilibrio", y por eso un cerebro entrenado es tan robusto.
"""
import os, pathlib, sys
import numpy as np
import onnxruntime as ort
import mujoco

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from panel_en_vivo import Panel, SinRuido, barra, cargar_demo, nombre_motor, spark
from leer_onnx import Cerebro

# --- PRUEBAS ---
CEREBRO = "alpha_walking"   # prueba "progresion_0_recien_nacido", "progresion_2_tambaleante", "progresion_4_mejor"
APAGAR_CAPA1 = 0.0          # prueba 0.5, 0.9, 0.99 y 1.0 (todas)

demo = cargar_demo(["--walking", f"policies/{CEREBRO}.onnx"])
panel = Panel()
estado = dict(caido=False, modelo=None, llamadas=0, cerebro=None, nombre="", pasos=None, accion=np.zeros(14))
cerebros = {}
mascara = (np.random.default_rng(0).random(512) >= APAGAR_CAPA1).astype(np.float32)


def agrupar(valores, grupos=48):
    """Resume cientos de neuronas en unas pocas barritas (la media de cada grupo)."""
    n = len(valores) // grupos
    return valores[: n * grupos].reshape(grupos, n).mean(axis=1)


class SesionEspia(ort.InferenceSession):
    """Una sesion de onnxruntime que, cada vez que el cerebro decide, repite la cuenta capa a capa para poder verla."""

    def __init__(self, ruta, *args, **kwargs):
        super().__init__(ruta, *args, **kwargs)
        self.ruta = str(ruta)

    def run(self, salidas, entradas, *args, **kwargs):
        nombre = next(iter(entradas))
        obs = np.array(entradas[nombre], dtype=np.float32)
        if obs.shape[-1] != 61:
            return super().run(salidas, entradas, *args, **kwargs)
        if self.ruta not in cerebros:
            cerebros[self.ruta] = Cerebro(self.ruta)
        cerebro = cerebros[self.ruta]
        pasos = cerebro.avanzar(obs, {0: mascara} if APAGAR_CAPA1 else None)
        accion = pasos[-1].astype(np.float32).reshape(1, -1)
        estado.update(cerebro=cerebro, nombre=self.ruta.replace("\\", "/").split("/")[-1], pasos=pasos, accion=accion.reshape(-1))
        estado["llamadas"] += 1
        if estado["llamadas"] % 10 == 0:
            dibujar()
        return [accion]


def fila(titulo, detalle, valores, escala=1.0, activas=True):
    texto = spark(agrupar(valores) if len(valores) > 48 else valores, escala)
    extra = f"  activas: {np.mean(valores > 0) * 100:3.0f} %" if activas else ""
    return f"  {titulo:<10}{detalle:<18}{texto}{extra}"


def dibujar():
    c, pasos = estado["cerebro"], estado["pasos"]
    if c is None or pasos is None:
        return
    lineas = [f"DENTRO DEL CEREBRO · {estado['nombre']} · {c.parametros():,} números (pesos) · una decisión cada 20 ms".replace(",", "."),
              f"decisión nº {estado['llamadas']}   (cada una = 4 pasos de física de 5 ms)   |   neuronas apagadas en la capa 1: {APAGAR_CAPA1 * 100:.0f} %", "",
              "          qué es            actividad de cada grupo de neuronas (▁ negativo · █ positivo)",
              fila("ENTRADA", "61 números", pasos[0], 2.0, activas=False) + "   ← (x − media) / desviación",
              fila("CAPA 1", "512 neuronas", pasos[1]) + "   ← pesos 512×61",
              fila("CAPA 2", "256 neuronas", pasos[2]) + "   ← pesos 256×512",
              fila("CAPA 3", "128 neuronas", pasos[3]) + "   ← pesos 128×256",
              fila("SALIDA", "14 órdenes", pasos[4], 0.8, activas=False) + "   ← pesos 14×128", "",
              "ÓRDENES (la salida, motor a motor)   -0.8 ◄── 0 ──► +0.8"]
    modelo = estado["modelo"]
    for i, valor in enumerate(estado["accion"]):
        nombre = nombre_motor(mujoco.mj_id2name(modelo, mujoco.mjtObj.mjOBJ_ACTUATOR, i)) if modelo else f"motor {i}"
        lineas.append(f"  {nombre:<22}{barra(valor, 0.8)}  {valor:+.2f}")
    lineas += ["", "  " + ("*** SE HA CAÍDO ***" if estado["caido"] else "De pie."),
               "Prueba: empuja al pato y mira qué capas reaccionan. Q para salir."]
    panel.mostrar(lineas, estado["llamadas"] / 50)


paso_real = mujoco.mj_step


def mj_step_con_nombres(modelo, datos, *args, **kwargs):
    estado["modelo"] = modelo
    estado["caido"] = bool(datos.qpos[2] < 0.07)
    return paso_real(modelo, datos, *args, **kwargs)


ort.InferenceSession = SesionEspia
mujoco.mj_step = mj_step_con_nombres
sys.stdout = SinRuido(sys.stdout)
demo.main()
sys.stdout.flush()
os._exit(0)  # evita un 'segmentation fault' de GLFW al cerrar el visor
