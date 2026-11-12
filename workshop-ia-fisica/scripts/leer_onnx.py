"""Lee un cerebro (.onnx) sin necesitar la libreria onnx: su arquitectura, sus pesos y lo que lleva escrito dentro.
Un fichero .onnx es un contenedor 'protobuf': este lector minimo basta para abrirlo y hacer la cuenta a mano con numpy.
No hace falta tocar este fichero: los ejercicios (n2_03) lo usan.
"""
import numpy as np


def _varint(b, i):
    r = s = 0
    while True:
        x = b[i]; i += 1
        r |= (x & 0x7F) << s; s += 7
        if not x & 0x80:
            return r, i


def _campos(b):
    i = 0
    while i < len(b):
        k, i = _varint(b, i)
        campo, tipo = k >> 3, k & 7
        if tipo == 0:
            v, i = _varint(b, i)
        elif tipo == 2:
            n, i = _varint(b, i); v = b[i:i + n]; i += n
        elif tipo == 1:
            v = b[i:i + 8]; i += 8
        elif tipo == 5:
            v = b[i:i + 4]; i += 4
        else:
            raise ValueError(f"tipo protobuf {tipo}")
        yield campo, v


def _tensor(b):
    dims, nombre, crudo = [], "", b""
    for campo, v in _campos(b):
        if campo == 1:
            dims.append(v)
        elif campo == 8:
            nombre = v.decode()
        elif campo == 9:
            crudo = v
    return nombre, np.frombuffer(crudo, dtype=np.float32).reshape(dims) if dims else np.frombuffer(crudo, dtype=np.float32)


class Cerebro:
    """Los pesos de un .onnx y la cuenta de la red: normalizar -> 3 capas ocultas con ELU -> 14 salidas."""

    def __init__(self, ruta):
        datos = open(ruta, "rb").read()
        grafo = next(v for c, v in _campos(datos) if c == 7)
        self.tensores = dict(_tensor(v) for c, v in _campos(grafo) if c == 5)
        self.metadatos = {}
        for c, v in _campos(datos):
            if c == 14:  # metadata_props: pares clave-valor
                par = dict(_campos(v))
                self.metadatos[par[1].decode()] = par[2].decode()
        t = self.tensores
        self.media = t["obs_normalizer._mean"].reshape(-1)
        self.divisor = next(v for k, v in t.items() if k.startswith("onnx::Div")).reshape(-1)
        self.capas = [(t[f"mlp.{i}.weight"], t[f"mlp.{i}.bias"]) for i in (0, 2, 4, 6)]

    def parametros(self):
        return sum(w.size + b.size for w, b in self.capas) + self.media.size + self.divisor.size

    def avanzar(self, obs, apagar=None):
        """Devuelve [entrada normalizada, capa1, capa2, capa3, salida]: lo que hay en cada punto de la red.
        apagar = {numero_de_capa: mascara de 0 y 1} deja a cero las neuronas que quieras (0 = primera capa)."""
        x = (np.asarray(obs, dtype=np.float32).reshape(-1) - self.media) / self.divisor
        pasos = [x]
        for n, (w, b) in enumerate(self.capas):
            x = w @ x + b
            if n < len(self.capas) - 1:
                x = np.where(x > 0, x, np.expm1(np.minimum(x, 0)))  # ELU
                if apagar and n in apagar:
                    x = x * apagar[n]
            pasos.append(x)
        return pasos
