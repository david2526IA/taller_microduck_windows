#!/usr/bin/env bash
# Lanza un entrenamiento corto (~10 min en una RTX 4090) para ver cómo aprende el robot.
# Uso:   ./entrenar.sh [Tarea] [iteraciones] [nombre]
#   Tareas fáciles de ver:  Mjlab-StandUp-Flat-MicroDuck (levantarse del suelo)
#                           Mjlab-Velocity-Flat-MicroDuck (andar, la tarea principal)
#                           Mjlab-Spin-Flat-MicroDuck (girar sobre patines)
#   Lista completa:         cd ~/microduck_rl && uv run list-envs
TAREA="${1:-Mjlab-StandUp-Flat-MicroDuck}"
ITER="${2:-300}"
NOMBRE="${3:-taller}"
PROYECTO="${PROYECTO:-$HOME/microduck_rl}"
cd "$PROYECTO" || { echo "No encuentro $PROYECTO. Lanza antes ./preparar_entrenamiento.sh"; exit 1; }

# Qué significa cada opción:
#   train <Tarea>                     qué va a aprender el robot
#   --env.scene.num-envs 4096         4096 robots simulados A LA VEZ en la GPU (más robots = aprende antes)
#   --agent.max-iterations $ITER      cuántas rondas de aprender (cada ronda = miles de pasos de simulación)
#   --agent.save-interval 25          guarda el "cerebro" cada 25 rondas: son los checkpoints (la progresión)
#   --agent.logger tensorboard        guarda la curva de aprendizaje en local (sin cuenta de wandb)
#   --agent.experiment-name           carpeta donde se guarda todo: logs/rsl_rl/<nombre>/
#   --video True --video-interval 50  graba un vídeo cada 50 rondas (pequeño: sirve para comprobar, no para enseñar)
echo "Entrenando $TAREA durante $ITER rondas. Cuando acabe, los cerebros estarán en:"
echo "   $PROYECTO/logs/rsl_rl/taller_$NOMBRE/"
MUJOCO_GL=egl uv run train "$TAREA" \
    --env.scene.num-envs 4096 \
    --agent.max-iterations "$ITER" \
    --agent.save-interval 25 \
    --agent.logger tensorboard \
    --agent.experiment-name "taller_$NOMBRE" \
    --agent.run-name "$(date +%H%M)" \
    --video True --video-length 250 --video-interval 50
