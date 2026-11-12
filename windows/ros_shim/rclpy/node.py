"""Nodo, publicadores, suscripciones y temporizadores: lo que en ROS 2 hace el middleware."""
import collections, threading, time

from .time import Time


class _Bus:
    """Cada topico tiene una lista de suscripciones. Publicar = meter el mensaje en la cola de cada una."""

    def __init__(self):
        self.subs = collections.defaultdict(list)
        self.last = {}            # ultimo mensaje por topico (QoS 'transient local', o 'latched')
        self.nodes = []
        self.lock = threading.Lock()

    def wake_all(self):
        for n in list(self.nodes):
            n._wake.set()


_BUS = _Bus()


class _Logger:
    def __init__(self, name):
        self.name = name

    def _p(self, nivel, m):
        print(f"[{nivel}] [{self.name}]: {m}", flush=True)

    def info(self, m, *a, **k): self._p("INFO", m)
    def warn(self, m, *a, **k): self._p("WARN", m)
    warning = warn
    def error(self, m, *a, **k): self._p("ERROR", m)
    def debug(self, m, *a, **k): pass


class _Clock:
    def now(self):
        return Time(time.time_ns())


class _Param:
    def __init__(self, value):
        self.value = value


class _Publisher:
    def __init__(self, topic, durable):
        self.topic, self.durable = topic, durable

    def publish(self, msg):
        with _BUS.lock:
            if self.durable:
                _BUS.last[self.topic] = msg
            subs = list(_BUS.subs[self.topic])
        for s in subs:
            s.push(msg)


class _Subscription:
    def __init__(self, node, cb, depth):
        self.node, self.cb = node, cb
        self.q = collections.deque(maxlen=max(1, depth))     # si el nodo va lento se descartan los mas viejos

    def push(self, msg):
        self.q.append(msg)
        self.node._wake.set()


class _Timer:
    def __init__(self, period, cb):
        self.period, self.cb = period, cb
        self.next = time.monotonic() + period


class Node:
    def __init__(self, name):
        self._name = name
        self._subs, self._timers, self._params = [], [], {}
        self._wake = threading.Event()
        self._logger = _Logger(name)
        self._clock = _Clock()
        _BUS.nodes.append(self)

    def get_name(self): return self._name
    def get_logger(self): return self._logger
    def get_clock(self): return self._clock

    def declare_parameter(self, name, default=None):
        import rclpy
        self._params[name] = _Param(rclpy._params.get(name, default))
        return self._params[name]

    def get_parameter(self, name):
        return self._params[name]

    def create_publisher(self, msg_type, topic, qos=10):
        return _Publisher(topic, getattr(qos, "durable", False))

    def create_subscription(self, msg_type, topic, cb, qos=10):
        s = _Subscription(self, cb, getattr(qos, "depth", qos if isinstance(qos, int) else 10))
        with _BUS.lock:
            _BUS.subs[topic].append(s)
            ultimo = _BUS.last.get(topic) if getattr(qos, "durable", False) else None
        self._subs.append(s)
        if ultimo is not None:
            s.push(ultimo)
        return s

    def create_timer(self, period_sec, cb):
        t = _Timer(period_sec, cb)
        self._timers.append(t)
        return t

    def destroy_node(self):
        with _BUS.lock:
            for lst in _BUS.subs.values():
                lst[:] = [s for s in lst if s.node is not self]
        if self in _BUS.nodes:
            _BUS.nodes.remove(self)
        return True

    def _spin_once(self, timeout):
        """Ejecuta los mensajes pendientes y los temporizadores vencidos (siempre en el hilo de este nodo)."""
        hecho = False
        for s in self._subs:
            while s.q:
                hecho = True
                s.cb(s.q.popleft())
        ahora = time.monotonic()
        for t in self._timers:
            if ahora >= t.next:
                t.next = ahora + t.period
                t.cb()
                hecho = True
        if not hecho:
            espera = timeout
            if self._timers:
                espera = min(espera, max(0.0, min(t.next for t in self._timers) - time.monotonic()))
            self._wake.wait(espera)
            self._wake.clear()
