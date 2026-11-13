"""CONFIGURA UN ENTRENAMIENTO REAL DE mjlab (sin GPU: aqui se prepara; se lanza en una maquina con GPU).

mjlab es la herramienta con la que se entrena el Microduck de verdad. Un entrenamiento se describe con:
   - una TAREA (el entorno: robot, mundo, observaciones, acciones, terminaciones, aleatorizacion),
   - la RECOMPENSA (una suma de terminos, cada uno con un peso)  <- lo que se edita casi siempre,
   - el ALGORITMO PPO (rondas, robots a la vez, tasa de aprendizaje, exploracion, gamma),
   - y DONDE se ejecuta (tu GPU, o una GPU en la nube).
Este modulo LEE la configuracion oficial, deja cambiar esas cosas y ESCRIBE un "paquete de entrenamiento" listo para ejecutar fuera del taller.

No se puede entrenar con mjlab en un PC sin GPU NVIDIA: lo que SI se puede (y se hace aqui) es todo lo anterior al boton de entrenar.
"""
import pathlib, re, sys, textwrap

RAIZ = pathlib.Path(__file__).resolve().parent.parent
OFICIAL = RAIZ / "rayuela-oficial"
REPO_OFICIAL = "https://github.com/Bravo-Robots/microduck_rl-rayuela"
RAMA_OFICIAL = "rayuela-ros2-humble"

# El "gancho" que se anade a la tarea para cambiar pesos SIN editar codigo (idea del proyecto patos_cuerda):
#   MICRODUCK_REWARD_WEIGHTS="termino=valor,otro*factor"    '=' fija el peso, '*' lo multiplica. Sin la variable, no cambia NADA.
GANCHO = '''    # Override opcional de pesos de recompensa por variable de entorno.  [gancho taller v1]
    import os as _os
    _rw = _os.environ.get("MICRODUCK_REWARD_WEIGHTS", "").strip()
    if _rw:
        for _kv in _rw.split(","):
            _kv = _kv.strip()
            if "*" in _kv:
                _k, _v = _kv.split("*"); _modo = "multiplicar"
            else:
                _k, _v = _kv.split("="); _modo = "fijar"
            _k = _k.strip()
            assert _k in cfg.rewards, f"recompensa desconocida: {_k} (hay: {sorted(cfg.rewards)})"
            _antes = cfg.rewards[_k].weight
            cfg.rewards[_k].weight = float(_v) if _modo == "fijar" else _antes * float(_v)
            print(f"[pesos] {_k}: {_antes} -> {cfg.rewards[_k].weight}")
    return cfg
'''

CASOS = {
    "voltereta": dict(
        titulo="La voltereta: una habilidad sencilla de describir, aprendida desde cero",
        tarea="Mjlab-Roulade-Flat-MicroDuck",
        tareas_extra=[],
        cfg="src/mjlab_microduck/tasks/microduck_roulade_env_cfg.py",
        funcion="make_microduck_roulade_env_cfg",
        resumen="El robot empieza de pie, rueda hacia delante sobre la cabeza y aterriza de pie otra vez. No hay reloj ni movimiento de referencia: "
                "el robot descubre solo COMO hacerlo, guiado unicamente por la recompensa. Cada episodio dura 5 s.",
        mundo="Suelo plano. Parte de pie, y una parte de los episodios empieza ya a mitad de la vuelta (curriculo inverso) para aprender "
              "primero el final. Aleatorizacion de centro de masa y orientacion del sensor (sim-to-real).",
        referencia="Entrenamiento real que has visto en n3_07 y n3_08: 20.750 rondas en varias tandas; la voltereta aparece sobre la ronda 750, "
                   "se vuelve irregular hacia la 3.000 y se estabiliza hacia la 11.000. La recompensa media paso de -0,9 a 35,3.",
        aqui_puedes="Ver y medir 9 checkpoints REALES de este entrenamiento: workshop-ia-fisica/exercises/n3_07_voltereta_checkpoints.py y n3_08_voltereta_medir.py.",
        trae_resultado="El .onnx se usa en la tecla R de n3_00 / n3_07 (parametro --roulade) y en la Rayuela oficial (roulade.onnx).",
        explicacion_recompensas={
            "roulade_progress": "premio por cada trozo de vuelta que gira hacia delante (la senal principal)",
            "roulade_overspeed": "castigo por girar a latigazos (demasiado rapido)",
            "roulade_head_pivot": "premio por apoyarse en la cabeza mientras gira",
            "roulade_landing_composite": "premio por acabar de pie (solo cuenta si ya dio la vuelta completa)",
            "roulade_upright_after_roll": "premio por acabar con el tronco vertical (tras la vuelta)",
            "roulade_height_after_roll": "premio por acabar a la altura de pie (tras la vuelta)",
            "roulade_landing_sharp": "premio fino por acabar casi perfecto: exige precision al final",
            "roulade_stand_tax": "castigo por quedarse agachado o tumbado tras la vuelta (obliga a levantarse)",
            "roulade_rise_velocity": "premio por subir con velocidad en el ultimo tramo (ayuda a levantarse)",
            "roulade_sagittal": "castigo por desviarse del plano de la vuelta (rodar recto, no por un hombro)",
            "roulade_lateral_vel": "castigo por moverse hacia los lados durante la vuelta",
            "roulade_flatness": "castigo por torcer el cuerpo durante la vuelta",
            "action_rate_l2": "castigo por mover los motores a tirones [lo sube un curriculo por etapas]",
            "joint_torque_rate_l2": "castigo por cambios bruscos de fuerza (0 al principio; se introduce mas tarde) [lo sube un curriculo por etapas]",
            "body_ang_vel": "castigo por girar el tronco rapido (casi 0: la voltereta ES un giro rapido)",
            "angular_momentum": "castigo por el momento angular (casi 0)",
            "arrival_damping": "castigo por llegar al suelo con prisa (0 al principio; el curriculo lo sube) [lo sube un curriculo por etapas]",
            "gentle_landing": "premio por aterrizar suave (peso positivo: la funcion ya devuelve un castigo) [lo sube un curriculo por etapas]",
            "self_collisions": "castigo por chocar una pieza del robot con otra",
        },
    ),
    "rayuela": dict(
        titulo="La Rayuela: aprender a patear la pelota a una casilla",
        tarea="Mjlab-BallKickSpeed-Right-Flat-MicroDuck",
        tareas_extra=["Mjlab-BallKickSpeed-Left-Flat-MicroDuck"],
        cfg="src/mjlab_microduck/tasks/microduck_ball_kick_speed_env_cfg.py",
        funcion="make_microduck_ball_kick_speed_env_cfg",
        resumen="El robot de pie aprende a patear la pelota con una VELOCIDAD DE SALIDA que se le ordena (cada casilla pide una). "
                "Hay una tarea por pie: entre las dos cubren todas las casillas.",
        mundo="Suelo plano, una pelota delante del pie, aleatorizacion de masa, rozamiento y empujones (sim-to-real).",
        referencia="BallKick: curriculo de pesos por etapas (el peso de cada termino cambia segun las iteraciones: ver KICK_*_STAGES en el fichero).",
        aqui_puedes="Entrenar de verdad una version pequena: exercises_rayuela/n3_05_entrena_la_patada.py (PPO en CPU, ~3 min) y jugar la partida con TU politica (n4_00).",
        trae_resultado="Una vez entrenada, el .onnx se usa en la Rayuela oficial (rayuela-oficial/policies-v1/ball_kick_speed_right.onnx es el oficial).",
    ),
    "patines": dict(
        titulo="Los patines: andar y patinar con ruedas bajo los pies",
        tarea="Mjlab-Velocity-Flat-MicroDuck-Rollers",
        tareas_extra=["Mjlab-RollerCrouch-Flat-MicroDuck", "Mjlab-RollerSlope-Flat-MicroDuck", "Mjlab-RollerStandUp-Flat-MicroDuck"],
        cfg="src/mjlab_microduck/tasks/microduck_velocity_rollers_env_cfg.py",
        funcion="make_microduck_velocity_rollers_env_cfg",
        resumen="Otro CUERPO (ruedas en los pies) con la misma tarea de seguir una orden de velocidad. Cambia la recompensa: "
                "ya no se premia levantar los pies, se premia deslizarse con el cuerpo estable.",
        mundo="Suelo plano; las ruedas cambian el contacto con el suelo, asi que hay que reajustar el rozamiento y la estabilidad.",
        referencia="Los documentos de rayuela-oficial/docs/ cuentan entrenamientos de patines de 8.000 a 15.000 iteraciones con 4.096 robots (sin cifras de tiempo).",
        aqui_puedes="Jugar con el cerebro de patines ya entrenado y romperlo con bateria baja y retraso de motores: exercises_rayuela/n4_02_patines.py.",
        trae_resultado="El .onnx resultante se carga igual que roller.onnx en n4_02_patines.py.",
    ),
    "obstaculos": dict(
        titulo="El circuito de obstaculos (estilo GTC Berlin): andar en terreno irregular",
        tarea="Mjlab-Velocity-Rough-MicroDuck",
        tareas_extra=["Mjlab-Velocity-Rough-Backlash-MicroDuck"],
        cfg="src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py",
        funcion="make_microduck_velocity_env_cfg",
        resumen="Andar siguiendo una orden de velocidad sobre TERRENO IRREGULAR (rampas, escalones pequenos, baldosas y escombros) con un "
                "curriculo: el terreno se hace mas dificil a medida que el robot mejora.",
        mundo="Terreno generado con dificultad creciente + aleatorizacion de dominio y holgura en las articulaciones (backlash).",
        referencia="Segun su ficha, rough_walk_g se entreno 3.300 iteraciones desde cero en terreno irregular; rough_walk_e, 800 afinando alpha_walking. "
                   "Para andar en llano, el README oficial dice ~1-2 h a 4.096 robots.",
        aqui_puedes="Ver y medir politicas ya entrenadas en el circuito en crescendo: exercises_rayuela/n4_05_obstaculos.py y n4_06_validar_politicas.py.",
        trae_resultado="El .onnx se pasa a n4_05 con CEREBRO = 'ruta/a/tu.onnx'.",
    ),
    "cuerda": dict(
        titulo="El duelo de la cuerda: dos robots que aprenden jugando entre si (autojuego)",
        tarea="Mjlab-ReachyTug-Flat-MicroDuck",
        tareas_extra=[],
        repo="https://github.com/david2526IA/microduck_rl", rama="tug-etapas",
        cfg=None,
        funcion=None,
        resumen="Dos patos atados por una cuerda; gana quien consigue que el otro cruce su linea o se caiga. UN solo cerebro juega los dos "
                "lados (el rival es una copia que se refresca cada 10 iteraciones). Se parte del cerebro de andar ya entrenado.",
        mundo="Dos robots, una cuerda (tendon), lineas de victoria, empate a los 20 s.",
        referencia="El entrenamiento real (proyecto patos_cuerda): 2.048 robots, 6.000 iteraciones desde el cerebro de andar model_10250, hasta la iteracion 6027.",
        aqui_puedes="Ver el duelo con el cerebro entrenado y cambiar fuerza y masa de cada pato: exercises_rayuela/n4_03_cuerda.py.",
        trae_resultado="El .onnx sustituye a windows/politicas/duelo2.onnx.",
        # Perfil de recompensas del duelo (proyecto patos_cuerda, carrera duelo2): editable con la misma variable de entorno.
        recompensas={"competitive_terminal": 200.0, "timeout_stalemate": -8.0, "fall_duel": 0.0, "fall_any": -20.0,
                     "pull_back_taut": 10.0, "rope_taut": 0.5, "tug_pull_velocity": 4.0},
        explicacion_recompensas={
            "competitive_terminal": "premio grande por GANAR (el rival cruza tu linea o cae)",
            "timeout_stalemate": "castigo si se acaba el tiempo en empate (obliga a atacar)",
            "fall_duel": "castigo si te caes durante el duelo (0: caerse ya pierde el duelo)",
            "fall_any": "castigo por caerte en cualquier momento",
            "pull_back_taut": "premio por tirar hacia atras con la cuerda tensa",
            "rope_taut": "pequeno premio por mantener la cuerda tensa",
            "tug_pull_velocity": "premio por la velocidad a la que tiras",
        },
    ),
}


# ----------------------------------------------------------------------------- leer la recompensa real
def _llamada_balanceada(texto, desde):
    """Devuelve el texto entre el parentesis que abre en 'desde' y su cierre."""
    prof = 0
    for i in range(desde, len(texto)):
        if texto[i] == "(":
            prof += 1
        elif texto[i] == ")":
            prof -= 1
            if prof == 0:
                return texto[desde + 1:i]
    return texto[desde + 1:]


def leer_recompensas(caso):
    """Lista de (termino, peso) que la tarea define o reajusta en su fichero oficial. Los demas se heredan de la tarea base."""
    c = CASOS[caso]
    if c.get("recompensas"):
        return list(c["recompensas"].items())
    texto = (OFICIAL / c["cfg"]).read_text(encoding="utf-8")
    a = texto.index(f"def {c['funcion']}(")
    cuerpo = texto[a:]
    encontrados = {}
    for m in re.finditer(r'cfg\.rewards\["(\w+)"\]\.weight\s*=\s*([^\s#]+)', cuerpo):
        encontrados[m.group(1)] = m.group(2)
    for m in re.finditer(r'cfg\.rewards\["(\w+)"\]\s*=\s*RewardTermCfg\(', cuerpo):
        inner = _llamada_balanceada(cuerpo, m.end() - 1)
        w = re.search(r"weight\s*=\s*([^,\n]+)", inner)
        if w:
            encontrados[m.group(1)] = w.group(1).strip()
    return [(k, _resolver(v, texto)) for k, v in encontrados.items()]


def _resolver(valor, texto):
    """Convierte 'KICK_AIM_STAGES[0]["weight"]' o 'KICK_AIM_WEIGHT' en numeros legibles (los pesos por etapas se muestran como 0 -> 4 -> 8)."""
    valor = valor.strip()
    consts = dict((m.group(1), m.group(2)) for m in re.finditer(r"^([A-Z][A-Z0-9_]+)\s*=\s*(-?\d[\d.]*(?:e-?\d+)?)", texto, re.M))
    etapas = re.match(r'(\w+)\[0\]\["weight"\]', valor)
    if etapas:
        bloque = re.search(etapas.group(1) + r"\s*=\s*\[(.*?)\n\]", texto, re.S)
        if bloque:
            vals = []
            for p in re.findall(r'"weight":\s*([^,}\s]+)', bloque.group(1)):
                vals.append(consts.get(p, p))
            return " -> ".join(vals) + "  (curriculo por etapas)"
    return consts.get(valor, valor)


def leer_constantes(caso):
    """Constantes numericas del fichero de la tarea (NOMBRE = valor  # comentario): los 'botones' que la tarea expone.
    Algunos pesos de recompensa se gobiernan desde aqui (por ejemplo, los pesos FINALES de un curriculo por etapas)."""
    c = CASOS[caso]
    if not c.get("cfg"):
        return []
    texto = (OFICIAL / c["cfg"]).read_text(encoding="utf-8")
    fin = texto.index(f"def {c['funcion']}(")
    res = []
    for m in re.finditer(r"^([A-Z][A-Z0-9_]+)\s*=\s*(-?\d[\d.]*(?:e-?\d+)?)[ \t]*(?:#[ \t]*(.*))?$", texto[:fin], re.M):
        res.append((m.group(1), m.group(2), (m.group(3) or "").strip()))
    return res


def mostrar_constantes(caso):
    cons = leer_constantes(caso)
    if not cons:
        return
    print("\n  CONSTANTES DE LA TAREA (botones que expone el fichero; algunas gobiernan pesos de recompensa o la aleatorizacion):")
    for nombre, valor, com in cons:
        print(f"  {nombre:34s} {valor:>10s}   {com[:60]}")


def mostrar_recompensas(caso):
    c = CASOS[caso]
    rec = leer_recompensas(caso)
    fuente = "perfil DUELO del proyecto patos_cuerda" if c.get("recompensas") else f"{c['cfg']} (rayuela-oficial)"
    print(f"\nRECOMPENSA de {c['tarea']}   [{fuente}]")
    print("  Cada termino puntua algo distinto; la nota del robot en cada paso es la SUMA de (termino x peso).")
    print(f"  {'termino':34s} {'peso':>10s}   que premia o castiga")
    expl = c.get("explicacion_recompensas", {})
    for nombre, peso in rec:
        print(f"  {nombre:34s} {peso:>10s}   {expl.get(nombre, '')}" if isinstance(peso, str) else f"  {nombre:34s} {peso:>10g}   {expl.get(nombre, '')}")
    if not c.get("recompensas"):
        print("  (Son los terminos que ESTA tarea anade o reajusta; el resto los hereda de la tarea base de andar.)")


# ----------------------------------------------------------------------------- el paquete de entrenamiento
def _pesos_a_texto(pesos):
    """{'upright': ('=', 2.0), 'x': ('*', 0.5)} o {'upright': 2.0} -> 'upright=2.0,x*0.5'."""
    partes = []
    for k, v in (pesos or {}).items():
        modo, val = v if isinstance(v, tuple) else ("=", v)
        partes.append(f"{k}{'*' if modo == '*' else '='}{val}")
    return ",".join(partes)


def comando_entrenar(caso, num_envs, iteraciones, guardar_cada, nombre, learning_rate=None, entropia=None, gamma=None, nube=False):
    c = CASOS[caso]
    op = [f"uv run train {c['tarea']}",
          f"--env.scene.num-envs {num_envs}",
          f"--agent.max-iterations {iteraciones}",
          f"--agent.save-interval {guardar_cada}",
          "--agent.logger tensorboard",
          f"--agent.experiment-name {nombre}"]
    if learning_rate is not None:
        op.append(f"--agent.algorithm.learning-rate {learning_rate}")
    if entropia is not None:
        op.append(f"--agent.algorithm.entropy-coef {entropia}")
    if gamma is not None:
        op.append(f"--agent.algorithm.gamma {gamma}")
    if nube:
        op.append("--hf-jobs")
    return " \\\n    ".join(op)


def aplicar_gancho(cfg_path, funcion):
    """Inserta el gancho de pesos justo antes del 'return cfg' de la funcion que construye la tarea. Idempotente. Devuelve el texto nuevo."""
    s = pathlib.Path(cfg_path).read_text(encoding="utf-8")
    if "[gancho taller v1]" in s:
        return s
    a = s.index(f"def {funcion}(")
    b = s.index("\n    return cfg\n", a)
    return s[:b + 1] + GANCHO + s[b + len("\n    return cfg\n"):]


SCRIPT_APLICAR = '''#!/usr/bin/env python3
"""Prepara el proyecto con TUS cambios:
  1. anade el gancho que deja cambiar pesos de recompensa con la variable MICRODUCK_REWARD_WEIGHTS (si no estaba);
  2. cambia las constantes de la tarea que elegiste en el taller.
Se ejecuta UNA vez, dentro del proyecto clonado:   python3 2_aplicar_pesos.py <carpeta_del_proyecto>
Hace una copia .bak del fichero y comprueba que sigue compilando."""
import py_compile, re, sys
from pathlib import Path
CFG = "{cfg}"
FUNCION = "{funcion}"
GANCHO = {gancho!r}
CONSTANTES = {constantes!r}
proj = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
f = proj / CFG
s = f.read_text(encoding="utf-8")
original = s
if "[gancho taller v1]" not in s:
    a = s.index("def " + FUNCION + "(")
    b = s.index("\\n    return cfg\\n", a)
    s = s[:b + 1] + GANCHO + s[b + len("\\n    return cfg\\n"):]
    print("gancho de pesos aplicado")
else:
    print("el gancho ya estaba aplicado")
for k, v in CONSTANTES.items():
    pat = re.compile(r"^(" + re.escape(k) + r"\\s*=\\s*)([^#\\n]*?)([ \\t]*(?:#.*)?)$", re.M)
    assert len(pat.findall(s)) == 1, "no encuentro la constante " + k + " (una sola vez) en " + str(f)
    antes = pat.search(s).group(2)
    s = pat.sub(lambda m: m.group(1) + repr(v) + m.group(3), s, count=1)
    print("constante", k + ":", antes, "->", repr(v))
if s != original:
    f.with_name(f.name + ".bak").write_text(original, encoding="utf-8")
    f.write_text(s, encoding="utf-8")
    py_compile.compile(str(f), doraise=True)
    print("OK:", f)
'''


def generar_paquete(caso, destino, num_envs=4096, iteraciones=1000, guardar_cada=50, nombre=None,
                    learning_rate=None, entropia=None, gamma=None, pesos=None, nube=False, constantes=None, variables_entorno=None):
    """Escribe en 'destino' todo lo necesario para lanzar este entrenamiento en una maquina con GPU. Devuelve la lista de ficheros."""
    c = CASOS[caso]
    d = pathlib.Path(destino)
    d.mkdir(parents=True, exist_ok=True)
    nombre = nombre or f"taller_{caso}"
    txt_pesos = _pesos_a_texto(pesos)
    repo, rama = c.get("repo", REPO_OFICIAL), c.get("rama", RAMA_OFICIAL)
    es_oficial = c.get("cfg") is not None
    escritos = []

    def w(nombre_f, contenido):
        p = d / nombre_f
        p.write_text(contenido.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
        escritos.append(p)

    w("1_preparar.sh", textwrap.dedent(f"""\
        #!/usr/bin/env bash
        # PASO 1: preparar la maquina (Ubuntu con GPU NVIDIA, o WSL2 con el driver de Windows). Una sola vez.
        set -e
        command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh        # uv: gestor de Python y librerias
        export UV_HTTP_TIMEOUT=600                                                          # las ruedas de CUDA pesan ~2 GB
        [ -d microduck_rl ] || git clone --branch {rama} {repo} microduck_rl
        cd microduck_rl
        uv sync                                                                             # instala mjlab, MuJoCo Warp, PyTorch (CUDA), RSL-RL...
        nvidia-smi | head -5                                                                # debe listar tu GPU
        uv run list-envs | grep -i "{c['tarea'].split('-')[1]}"                             # la tarea debe aparecer
        echo "Listo. Siguiente: 2_aplicar_pesos.py (si cambias pesos) y 3_probar.sh"
        """))
    if es_oficial:
        w("2_aplicar_pesos.py", SCRIPT_APLICAR.format(cfg=c["cfg"], funcion=c["funcion"], gancho=GANCHO, constantes=dict(constantes or {})))
    else:
        w("2_aplicar_pesos.py", textwrap.dedent(f"""\
            #!/usr/bin/env python3
            # En el duelo, el gancho de pesos YA lo trae el proyecto patos_cuerda (scripts/parches/aplicar_rewards.py).
            # Ese proyecto aplica ademas otros parches (reglas del duelo, victoria por cruce de linea, refresco del rival...).
            print("Aplica los parches de patos_cuerda sobre microduck_rl (rama {rama}); ver su LEEME.md. El gancho de pesos va incluido.")
            """))
    extra_env = ""
    if not es_oficial:
        v = {"MICRODUCK_OPPONENT_INTERVAL": 10, "MICRODUCK_SPAWN_OFFSET": 0.45, **(variables_entorno or {})}
        extra_env = textwrap.dedent(f"""\
            # Autojuego: parte del cerebro de andar ya entrenado y juega contra una copia de si mismo que se refresca cada N iteraciones.
            export MICRODUCK_BASE_CHECKPOINT=checkpoints/locomocion_10250/model_10250.pt
            export MICRODUCK_OPPONENT_CHECKPOINT="$MICRODUCK_BASE_CHECKPOINT" MICRODUCK_OPPONENT_POOL=0
            export MICRODUCK_OPPONENT_INTERVAL={v['MICRODUCK_OPPONENT_INTERVAL']}   # cada cuantas iteraciones se refresca el rival
            export MICRODUCK_SPAWN_OFFSET={v['MICRODUCK_SPAWN_OFFSET']}             # lo cerca de la linea que empiezan (mas cerca = el duelo empieza antes)
            """)
    entorno = (f'export MICRODUCK_REWARD_WEIGHTS="{txt_pesos}"\n' if txt_pesos else "# (sin cambios de pesos: se usa la recompensa original)\n")
    w("3_probar.sh", textwrap.dedent(f"""\
        #!/usr/bin/env bash
        # PASO 3: PRUEBA DE HUMO. Siempre antes del entrenamiento largo: 64 robots, 5 iteraciones. Si falla aqui, falla en la prueba y no a las 2 horas.
        cd microduck_rl
        {entorno.strip()}
        """) + extra_env.replace("\n", "\n") + textwrap.dedent(f"""\
        uv run train {c['tarea']} --env.scene.num-envs 64 --agent.max-iterations 5 --agent.logger tensorboard
        echo "Si no hubo errores y la recompensa aparece en el log, lanza 4_entrenar.sh"
        """))
    w("4_entrenar.sh", textwrap.dedent(f"""\
        #!/usr/bin/env bash
        # PASO 4: ENTRENAR (en tu GPU). {c['titulo']}
        cd microduck_rl
        {entorno.strip()}
        """) + extra_env + comando_entrenar(caso, num_envs, iteraciones, guardar_cada, nombre, learning_rate, entropia, gamma) + "\n")
    w("4b_entrenar_en_la_nube.sh", textwrap.dedent(f"""\
        #!/usr/bin/env bash
        # PASO 4 (alternativa): sin GPU propia, se envia a un Hugging Face Job (GPU en la nube; hace falta cuenta y `hf auth login`).
        # Cuesta dinero segun la GPU que elijas: mira el precio en Hugging Face ANTES de lanzar.
        cd microduck_rl
        {entorno.strip()}
        """) + extra_env + comando_entrenar(caso, num_envs, iteraciones, guardar_cada, nombre, learning_rate, entropia, gamma, nube=True) + "\n")
    w("LEEME.md", textwrap.dedent(f"""\
        # Tu paquete de entrenamiento: {c['titulo']}

        Generado en el taller. Tarea de mjlab: **`{c['tarea']}`**   ·   Repositorio: {repo} (rama `{rama}`)

        ## Lo que has configurado
        | Opcion | Valor | Que significa |
        |---|---|---|
        | robots a la vez | {num_envs} | mas robots = mas experiencia por minuto (y mas memoria de GPU; si no cabe, baja a 2048 o 1024) |
        | rondas (iteraciones) | {iteraciones} | cuantas veces se repite "probar, puntuar, ajustar" |
        | guardar cada | {guardar_cada} | cada cuantas rondas se guarda el cerebro (los checkpoints: la progresion) |
        | tasa de aprendizaje | {learning_rate if learning_rate is not None else 'la de la tarea'} | tamano de cada ajuste |
        | exploracion (entropia) | {entropia if entropia is not None else 'la de la tarea'} | cuanto prueba cosas raras |
        | gamma | {gamma if gamma is not None else 'la de la tarea'} | cuanto piensa en el futuro |
        | pesos de recompensa cambiados | {txt_pesos or 'ninguno'} | `termino=valor` fija el peso; `termino*factor` lo multiplica |
        | constantes de la tarea cambiadas | {', '.join(f'{k}={v}' for k, v in dict(constantes or dict()).items()) or 'ninguna'} | se escriben en el fichero de la tarea con `2_aplicar_pesos.py` |

        ## Como se lanza (en una maquina con GPU NVIDIA)
        1. `bash 1_preparar.sh`  (una vez; descarga ~2 GB)
        2. `python3 2_aplicar_pesos.py microduck_rl`  (solo si has cambiado pesos)
        3. `bash 3_probar.sh`  (prueba de humo: 64 robots, 5 rondas)
        4. `bash 4_entrenar.sh`  (o `4b_entrenar_en_la_nube.sh` si no tienes GPU)
        5. Mirar la curva: `uv run tensorboard --logdir logs/rsl_rl` y abrir el navegador. Si `Train/mean_reward` SUBE, esta aprendiendo.

        ## Que se espera del resultado
        {c['referencia']}
        Para vigilar: que la recompensa media suba, que el robot aguante mas pasos antes de caerse, y que ningun termino de castigo quede en positivo.

        ## Traerlo de vuelta
        El entrenamiento exporta un `.onnx` al terminar (carpeta `logs/rsl_rl/{nombre}/...`). {c['trae_resultado']}
        Para un checkpoint intermedio: `uv run python scripts/export.py` (ver el README del proyecto).

        ## Que NO esta verificado
        Este paquete se genero sin GPU ni mjlab instalado: no se ha ejecutado aqui. Las opciones de `uv run train` son las que documenta el proyecto.
        Por eso existe el paso 3 (prueba de humo): hazlo siempre antes del entrenamiento largo.
        """))
    return escritos


def principal(caso, **kw):
    """Lo que hace cada ejercicio n6_*: muestra la tarea, la recompensa real, y escribe el paquete."""
    c = CASOS[caso]
    for f in (sys.stdout, sys.stderr):
        f.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 100)
    print(c["titulo"])
    print("=" * 100)
    print(f"\n1) LA TAREA: {c['tarea']}" + (f"  (y {', '.join(c['tareas_extra'])})" if c["tareas_extra"] else ""))
    print(textwrap.fill(c["resumen"], 98, initial_indent="   ", subsequent_indent="   "))
    print(textwrap.fill("El mundo: " + c["mundo"], 98, initial_indent="   ", subsequent_indent="   "))
    print("\n2) LA RECOMPENSA REAL (lo que el robot 'quiere'):", end="")
    mostrar_recompensas(caso)
    mostrar_constantes(caso)
    print("\n3) TUS CAMBIOS:")
    pesos = kw.get("pesos")
    print(f"   robots a la vez {kw.get('num_envs', 4096)} | rondas {kw.get('iteraciones', 1000)} | pesos cambiados: {_pesos_a_texto(pesos) or 'ninguno'}")
    if kw.get("constantes"):
        validas = {n for n, _, _ in leer_constantes(caso)}
        print("   constantes de la tarea cambiadas:", ", ".join(f"{k}={v}" for k, v in kw["constantes"].items()))
        for k in kw["constantes"]:
            if k not in validas:
                print(f"   AVISO: '{k}' no esta en la lista de constantes de arriba; el script de preparacion se parara al no encontrarla.")
    if pesos and caso != "cuerda":
        nombres = [n for n, _ in leer_recompensas(caso)]
        for k in pesos:
            if k not in nombres:
                print(f"   AVISO: '{k}' no esta en la lista de arriba (puede venir de la tarea base). Si no existe, el entrenamiento se parara al empezar.")
    elif pesos:
        for k in pesos:
            if k not in c["recompensas"]:
                print(f"   AVISO: '{k}' no es un termino del duelo.")
    destino = kw.pop("destino", RAIZ / "mi_entrenamiento" / caso)
    fich = generar_paquete(caso, destino, **kw)
    print(f"\n4) TU PAQUETE: {pathlib.Path(destino).relative_to(RAIZ) if str(destino).startswith(str(RAIZ)) else destino}")
    for f in fich:
        print("   -", f.name)
    print("\n   El comando de entrenamiento que has configurado:\n")
    print(textwrap.indent(comando_entrenar(caso, kw.get("num_envs", 4096), kw.get("iteraciones", 1000), kw.get("guardar_cada", 50),
                                           kw.get("nombre") or f"taller_{caso}", kw.get("learning_rate"), kw.get("entropia"), kw.get("gamma")), "      "))
    print("\n5) Y AQUI, SIN GPU:", c["aqui_puedes"])
    print("\n   Lo que has hecho es lo mismo que se hace antes de un entrenamiento real: elegir la tarea, leer y ajustar la recompensa,")
    print("   elegir cuanta experiencia y cuantas rondas, y dejarlo listo para lanzar. Solo falta una GPU y el boton de entrenar.")
    return fich
