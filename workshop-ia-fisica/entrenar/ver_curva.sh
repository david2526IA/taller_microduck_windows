#!/usr/bin/env bash
# Abre la curva de aprendizaje en el navegador (http://localhost:6006), durante el entrenamiento o después.
# Uso:   ./ver_curva.sh [nombre]      (el mismo nombre que en ./entrenar.sh; por defecto "taller")
NOMBRE="${1:-taller}"
PROYECTO="${PROYECTO:-$HOME/microduck_rl}"
cd "$PROYECTO" || exit 1
echo "Abre http://localhost:6006 -> pestaña SCALARS."
echo "  Train/mean_reward         = puntos medios por intento. Si SUBE, el robot está aprendiendo."
echo "  Train/mean_episode_length = cuánto aguanta antes de acabar el intento (sube cuando ya no se cae)."
uv run tensorboard --logdir "logs/rsl_rl/taller_$NOMBRE" --port 6006
