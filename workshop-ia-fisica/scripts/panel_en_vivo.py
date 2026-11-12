"""Ayudas para los ejercicios "en vivo": cargan la demo con el pato y dibujan un panel en la terminal.
No hace falta tocar este fichero: los ejercicios (n2_00, n2_01) lo usan.
"""
import importlib.util, os, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BARRAS = "▁▂▃▄▅▆▇█"


def cargar_demo(argv_extra=()):
    """Carga scripts/infer_policy.py (la demo con cerebro) y prepara sus opciones."""
    os.chdir(RAIZ)
    sys.path.insert(0, str(RAIZ / "scripts"))
    spec = importlib.util.spec_from_file_location("infer_policy", RAIZ / "scripts" / "infer_policy.py")
    demo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo)
    sys.argv = ["infer_policy", "--walking", "policies/alpha_walking.onnx", "--standing", "policies/alpha_stand.onnx",
                "--new-cmd-obs", *argv_extra]
    return demo


def spark(valores, escala):
    """Una fila de barritas, una por valor. Alto = valor positivo grande, bajo = negativo."""
    salida = ""
    for v in valores:
        nivel = int(min(max((v / escala + 1) / 2, 0.0), 0.999) * len(BARRAS))
        salida += BARRAS[nivel]
    return salida


def barra(valor, escala, ancho=20):
    """Barra centrada en cero: ·····|█████····· (negativa a la izquierda, positiva a la derecha)."""
    mitad = ancho // 2
    n = int(round(min(abs(valor) / escala, 1.0) * mitad))
    if valor >= 0:
        return "·" * mitad + "|" + "█" * n + "·" * (mitad - n)
    return "·" * (mitad - n) + "█" * n + "|" + "·" * mitad


def barra_positiva(valor, ancho=20):
    """Barra de 0 a 1: █████·····"""
    n = int(round(min(max(valor, 0.0), 1.0) * ancho))
    return "█" * n + "·" * (ancho - n)


class Panel:
    """Dibuja un bloque de texto que se refresca en el mismo sitio de la terminal."""

    def __init__(self):
        self.tty = sys.stdout.isatty()
        self.ultimo = -99.0
        if os.name == "nt":
            os.system("")  # activa los codigos ANSI en la terminal de Windows
        if self.tty:
            sys.stdout.write("\033[2J")

    def mostrar(self, lineas, t):
        if self.tty:
            sys.stdout.write("\033[H" + "".join(l[:110] + "\033[K\n" for l in lineas) + "\033[J")
            sys.stdout.flush()
        elif t - self.ultimo >= 5:          # sin terminal (pruebas): un bloque cada 5 s
            self.ultimo = t
            print("\n".join(lineas), flush=True)


class SinRuido:
    """Quita la linea de velocidad que la demo imprime cada segundo, para que se lea el panel."""

    def __init__(self, destino):
        self.destino = destino

    def write(self, texto):
        if "[vel 1s avg]" not in texto:
            self.destino.write(texto)

    def flush(self):
        self.destino.flush()

    def __getattr__(self, nombre):
        return getattr(self.destino, nombre)


NOMBRES = {"hip_yaw": "cadera (giro)", "hip_roll": "cadera (lado)", "hip_pitch": "cadera", "knee": "rodilla",
           "ankle": "tobillo", "neck_pitch": "cuello", "head_pitch": "cabeza (asiente)", "head_yaw": "cabeza (gira)",
           "head_roll": "cabeza (inclina)"}


def nombre_motor(nombre_mjcf):
    lado = "izq." if nombre_mjcf.startswith("left_") else "der." if nombre_mjcf.startswith("right_") else ""
    base = nombre_mjcf.replace("left_", "").replace("right_", "")
    return f"{NOMBRES.get(base, base)} {lado}".strip()
