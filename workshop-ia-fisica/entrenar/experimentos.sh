#!/usr/bin/env bash
# Entrena la MISMA tarea 6 veces cambiando UN solo parametro cada vez (100 rondas, misma semilla),
# para comparar las curvas. Son los datos del ejercicio n3_04 del taller (entrenar/resultados/). ~20 min en una RTX 4090.
# Uso:  ./experimentos.sh        (los resultados quedan en logs/rsl_rl/exp_<nombre>/)
PROYECTO="${PROYECTO:-$HOME/microduck_rl}"
cd "$PROYECTO" || exit 1
TAREA=Mjlab-StandUp-Flat-MicroDuck
BASE=(--agent.max-iterations 100 --agent.save-interval 100 --agent.logger tensorboard --env.seed 1 --agent.seed 1)

correr() {   # correr <nombre> [parametros extra...]
    local nombre=$1; shift
    echo "=== $nombre: $* ($(date +%H:%M:%S))"
    MUJOCO_GL=egl .venv/bin/train "$TAREA" --env.scene.num-envs 4096 "${BASE[@]}" \
        --agent.experiment-name "exp_$nombre" --agent.run-name "$nombre" "$@" > "logs/exp_$nombre.log" 2>&1
    echo "    terminado con codigo $? ($(date +%H:%M:%S))"
}

mkdir -p logs
correr base
correr pocos_robots   --env.scene.num-envs 256
correr lr_alto        --agent.algorithm.schedule fixed --agent.algorithm.learning-rate 0.01
correr lr_bajo        --agent.algorithm.schedule fixed --agent.algorithm.learning-rate 0.00005
correr exploracion    --agent.algorithm.entropy-coef 0.1
correr miopia         --agent.algorithm.gamma 0.8
echo "TODOS LOS EXPERIMENTOS TERMINADOS"
