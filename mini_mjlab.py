"""MINI-MJLAB: los verbos de mjlab (list-envs, params, play, train, validate) para un PC SIN GPU.

mjlab es la herramienta con la que se entrena el Microduck de verdad: `uv run list-envs`, `uv run train <entorno>`,
`uv run play <entorno>` (necesita GPU NVIDIA). Aqui tienes lo mismo, en pequeño y en CPU, sobre los escenarios del taller:
cada "entorno" es uno de los ejercicios, y los parametros se cambian desde la linea de comandos SIN editar el fichero.

   MJLAB list-envs                                         lista los entornos y que se puede hacer con cada uno
   MJLAB params  Mini-Obstacles-MicroDuck                  muestra los parametros que se pueden cambiar (y su valor)
   MJLAB play    Mini-Obstacles-MicroDuck --set NIVEL=3 --set CEREBRO=rough_walk_e
   MJLAB train   Mini-Kick-MicroDuck --set ITERACIONES=40 --set LEARNING_RATE=0.02
   MJLAB validate Mini-Obstacles-MicroDuck --set PRUEBAS=10

(Doble clic en MJLAB.bat abre una consola con este programa; o:  workshop-ia-fisica\\.venv\\Scripts\\python.exe mini_mjlab.py list-envs)
"""
import ast, pathlib, re, sys

for _f in (sys.stdout, sys.stderr):
    _f.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parent
EJ = RAIZ / "exercises_rayuela"
TALLER = RAIZ / "workshop-ia-fisica" / "exercises"

# id : (titulo, jugar, entrenar, validar, equivalente en mjlab / Isaac Lab)
ENTORNOS = {
    "Mini-Scene-MicroDuck": ("Tu propia escena: gravedad, rozamiento, masas, obstaculos", EJ / "n1_02_tu_escena.py", None, None,
                             "escena MJCF personalizada (spec_fn de mjlab)"),
    "Mini-Kick-MicroDuck": ("Rayuela: patear la pelota a una casilla", EJ / "n4_00_partida_rayuela.py", EJ / "n3_05_entrena_la_patada.py", None,
                            "Mjlab-BallKickSpeed-{Left,Right}-Flat-MicroDuck + el juego de Bravo Robots"),
    "Mini-Obstacles-MicroDuck": ("Circuito de obstaculos (GTC Berlin): rampa, escalones, cuadricula, escombros",
                                 EJ / "n4_05_obstaculos.py", None, EJ / "n4_06_validar_politicas.py",
                                 "IsaacContrib-Velocity-Rough-MicroDuck (Isaac Lab)"),
    "Mini-TugOfWar-MicroDuck": ("Duelo de la cuerda con politica entrenada (autojuego)", EJ / "n4_03_cuerda.py", None, None,
                                "Mjlab-ReachyTug-Flat-MicroDuck (proyecto patos_cuerda)"),
    "Mini-Balance-MicroDuck": ("Laboratorio de equilibrio: empujones, postura del cuerpo, balancin", EJ / "n4_04_equilibrio.py", None, None,
                               "Mjlab-Velocity-Flat-MicroDuck con empujones aleatorios (push_by_setting_velocity)"),
    "Mini-Skates-MicroDuck": ("Patines: otro cuerpo, otro cerebro", EJ / "n4_02_patines.py", None, None,
                              "Mjlab-Velocity-Flat-MicroDuck-Rollers"),
    "Mini-Rayuela-ROS2-MicroDuck": ("ROS 2 en vivo: nodos y topics de la Rayuela", EJ / "n4_01_ros2_en_vivo.py", None, None,
                                    "ros2 launch rayuela rayuela.launch.py"),
}


def valor_literal(txt):
    try:
        return repr(ast.literal_eval(txt))
    except Exception:
        return repr(txt)                       # sin comillas: se toma como texto (p. ej. CEREBRO=rough_walk_e)


def parametros(src):
    """(nombre, valor, descripcion) de las constantes de la zona PARAMETROS de un ejercicio (entre las dos lineas de '=')."""
    ini = re.search(r"^# =+ PARAMETROS.*$", src, re.M)
    zona = src
    if ini:
        resto = src[ini.end():]
        fin = re.search(r"^# =+\s*$", resto, re.M)
        zona = resto[:fin.start()] if fin else resto
    out, comentario = [], []
    for linea in zona.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9_]*)\s*=\s*(.+?)(\s+#.*)?$", linea)
        if m:
            desc = next((c.lstrip("# ").strip() for c in comentario if not c.startswith("# ---") and "AFECTA" not in c), "")
            out.append((m.group(1), m.group(2).strip(), desc))
            comentario = []
        elif linea.startswith("#"):
            comentario.append(linea)
        elif not linea.strip():
            comentario = []
    return out


def aplicar(src, cambios):
    for k, v in cambios.items():
        pat = re.compile(rf"^({re.escape(k)}\s*=\s*)(.+?)(\s+#.*)?$", re.M)
        if not pat.search(src):
            validos = ", ".join(n for n, _, _ in parametros(src))
            raise SystemExit(f"El parametro '{k}' no existe. Parametros validos: {validos}")
        src = pat.sub(lambda m: m.group(1) + valor_literal(v) + (m.group(3) or ""), src, count=1)
    return src


def lanzar(ruta, cambios):
    src = ruta.read_text(encoding="utf-8")
    if cambios:
        src = aplicar(src, cambios)
        print("Parametros cambiados:", ", ".join(f"{k} = {valor_literal(v)}" for k, v in cambios.items()), "\n", flush=True)
    sys.argv = [str(ruta)]
    g = {"__name__": "__main__", "__file__": str(ruta)}
    exec(compile(src, str(ruta), "exec"), g)


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "help"):
        print(__doc__)
        return
    cmd = a[0]
    cambios = {}
    resto = []
    i = 1
    while i < len(a):
        if a[i] == "--set" and i + 1 < len(a) and "=" in a[i + 1]:
            k, v = a[i + 1].split("=", 1)
            cambios[k.strip()] = v.strip()
            i += 2
        else:
            resto.append(a[i])
            i += 1
    if cmd == "list-envs":
        print(f"{'ENTORNO':30s} {'COMANDOS':22s} QUE ES  (equivalente real)")
        for k, (t, jug, ent, val, eq) in ENTORNOS.items():
            cm = "/".join(c for c, x in (("play", jug), ("train", ent), ("validate", val)) if x)
            print(f"{k:30s} {cm:22s} {t}\n{'':53s}real: {eq}")
        return
    if not resto or resto[0] not in ENTORNOS:
        sys.exit(f"Falta el entorno. Prueba: MJLAB list-envs")
    t, jug, ent, val, eq = ENTORNOS[resto[0]]
    if cmd == "params":
        ruta = jug
        print(f"Parametros de {resto[0]}  ({ruta.name}) - se cambian con --set NOMBRE=VALOR\n")
        for n, v, d in parametros(ruta.read_text(encoding="utf-8")):
            print(f"  {n:24s} = {v[:48]:48s} {d[:70]}")
        return
    destino = {"play": jug, "train": ent, "validate": val}.get(cmd)
    if destino is None:
        sys.exit(f"'{cmd}' no esta disponible para {resto[0]}. Comandos de este entorno: " +
                 "/".join(c for c, x in (("play", jug), ("train", ent), ("validate", val)) if x))
    lanzar(destino, cambios)


if __name__ == "__main__":
    main()
