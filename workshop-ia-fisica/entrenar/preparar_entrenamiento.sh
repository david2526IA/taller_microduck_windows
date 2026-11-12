#!/usr/bin/env bash
# Deja listo el ENTORNO DE ENTRENAMIENTO del Microduck, explicando cada paso.
# Requiere: Linux (o Windows con WSL2) y una GPU NVIDIA. Se puede repetir sin problema.
#
# Uso:   ./preparar_entrenamiento.sh                 (instala en ~/microduck_rl)
#        DESTINO=/otra/ruta ./preparar_entrenamiento.sh
set -u
DESTINO="${DESTINO:-$HOME/microduck_rl}"
REPO="https://github.com/pollen-robotics/microduck_rl"

paso()    { echo; echo "=== PASO $1: $2"; }
que()     { echo "    Qué hace: $1"; }
porque()  { echo "    Para qué: $1"; }
ok()      { echo "    ✔ $1"; }
fallo()   { echo "    ✘ $1"; echo; echo "Corrige esto y vuelve a lanzar el script (no se pierde nada de lo hecho)."; exit 1; }

echo "Preparando el entorno de entrenamiento en: $DESTINO"

paso 1 "Comprobar la GPU NVIDIA"
que "Pregunta al driver de NVIDIA qué tarjeta hay (comando nvidia-smi)."
porque "Entrenar necesita una GPU: simula miles de robots a la vez. Sin ella tardaría días."
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1; then
    ok "$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1)"
else
    fallo "No veo ninguna GPU NVIDIA. Instala el driver de NVIDIA (en Windows, usa WSL2 con el driver de Windows)."
fi

paso 2 "Comprobar git y uv"
que "uv es el gestor que instala Python y todas las librerías del proyecto en una carpeta aislada (.venv)."
porque "Así no se mezcla con nada de tu sistema, y todos tenemos exactamente las mismas versiones."
command -v git >/dev/null 2>&1 || fallo "Falta git. Instálalo con: sudo apt install git"
ok "git: $(git --version)"
if ! command -v uv >/dev/null 2>&1; then
    echo "    uv no está instalado. Lo instalo ahora (script oficial de astral.sh)."
    curl -LsSf https://astral.sh/uv/install.sh | sh || fallo "No se pudo instalar uv."
    export PATH="$HOME/.local/bin:$PATH"
fi
ok "uv: $(uv --version)"

paso 3 "Descargar el proyecto de entrenamiento"
que "Clona microduck_rl, el proyecto de Pollen Robotics con las tareas, las recompensas y el entrenador."
porque "Contiene lo que el robot aprende: cada tarea (andar, levantarse, patinar...) es una carpeta con sus reglas."
if [ -d "$DESTINO/.git" ] || [ -f "$DESTINO/pyproject.toml" ]; then
    ok "Ya existe en $DESTINO, no lo vuelvo a descargar."
else
    git clone "$REPO" "$DESTINO" || fallo "No se pudo clonar $REPO (¿hay internet?)."
    ok "Descargado."
fi
cd "$DESTINO" || fallo "No puedo entrar en $DESTINO."

paso 4 "Instalar las librerías (uv sync)"
que "Crea la carpeta .venv e instala Python 3.12, PyTorch con CUDA, MuJoCo Warp, mjlab, ONNX y el modelo de motores BAM."
porque "Son ~2 GB la primera vez. Si la conexión es lenta, uv podía abortar: por eso subo su tiempo de espera."
UV_HTTP_TIMEOUT=600 uv sync || fallo "uv sync falló. Mira el mensaje de arriba y repite."
ok "Librerías instaladas en $DESTINO/.venv"

paso 5 "Comprobar que PyTorch ve la GPU"
que "Pide a PyTorch que use CUDA (el lenguaje de la GPU NVIDIA)."
porque "Si esto falla, el entrenamiento arrancaría pero iría con la CPU, miles de veces más lento."
.venv/bin/python - <<'PY' || fallo "PyTorch no detecta CUDA. Revisa el driver de NVIDIA."
import torch
assert torch.cuda.is_available(), "sin CUDA"
print("    ✔ PyTorch", torch.__version__, "usando", torch.cuda.get_device_name(0))
PY

paso 6 "Ver las tareas disponibles"
que "Lista las tareas registradas (uv run list-envs). Cada una es «algo que el robot puede aprender»."
porque "El nombre de la tarea es lo único que le dices a 'train' para elegir qué aprender."
uv run list-envs 2>/dev/null | grep -i "microduck" | head -40 || true

paso 7 "Prueba rápida (30 segundos)"
que "Entrena 3 rondas con solo 64 robots para comprobar que todo el circuito funciona."
porque "Mejor descubrir un fallo ahora que cuando lances el entrenamiento de verdad."
if MUJOCO_GL=egl uv run train Mjlab-StandUp-Flat-MicroDuck --env.scene.num-envs 64 \
       --agent.max-iterations 3 --agent.logger tensorboard \
       --agent.experiment-name prueba_instalacion --agent.run-name prueba >/tmp/prueba_entrenamiento.log 2>&1; then
    ok "El entrenamiento arranca y termina bien."
    rm -rf logs/rsl_rl/prueba_instalacion
else
    echo "    Últimas líneas del registro (/tmp/prueba_entrenamiento.log):"; tail -8 /tmp/prueba_entrenamiento.log
    fallo "La prueba rápida falló."
fi

echo
echo "TODO LISTO. Entorno en: $DESTINO"
echo "Siguiente paso:   ./entrenar.sh        (entrena ~10 min)   y en otra terminal:   ./ver_curva.sh"
