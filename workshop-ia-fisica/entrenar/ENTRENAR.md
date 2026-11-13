# Entrenar tu propio cerebro (con una GPU NVIDIA)

En el taller usamos cerebros ya entrenados. Esta carpeta te enseña **cómo se entrena uno**, paso a paso, para que
entiendas qué hay detrás de cada fichero `.onnx`. Hace falta **Linux (o Windows con WSL2) y una GPU NVIDIA**.
No hace falta hacerlo en el taller: aquí está todo explicado.

## Los tres pasos

| Paso | Comando | Qué pasa |
|---|---|---|
| 1. Preparar | `./preparar_entrenamiento.sh` | Instala todo y comprueba que la GPU funciona (explica cada paso en pantalla). Una sola vez. |
| 2. Entrenar | `./entrenar.sh` | Miles de robots simulados aprenden a la vez. ~10 min en una RTX 4090. |
| 3. Mirar | `./ver_curva.sh` | Abre la curva de aprendizaje en el navegador. |

## Qué instala el paso 1 (y para qué)

| Pieza | Qué es | Para qué |
|---|---|---|
| **uv** | Gestor de Python y librerías | Todos tenemos las mismas versiones, en una carpeta aislada (`.venv`). |
| **microduck_rl** | Proyecto de Pollen Robotics | Las tareas del robot, sus recompensas y el entrenador. |
| **mjlab + MuJoCo Warp** | Simulador que corre en la GPU | Simula miles de robots a la vez. |
| **PyTorch (CUDA)** | La red neuronal | El cerebro que aprende; CUDA es el lenguaje de la GPU NVIDIA. |
| **PPO (RSL-RL)** | El algoritmo de aprendizaje | Decide cómo ajustar el cerebro tras cada ronda de intentos. |
| **BAM** | Modelo de los motores reales | Que los motores simulados se comporten como los de verdad. |
| **ONNX Runtime** | Lector de cerebros | Es lo que usa el simulador del taller para ejecutar un `.onnx`. |

## Qué significa cada opción de `entrenar.sh`

```
uv run train Mjlab-StandUp-Flat-MicroDuck \
    --env.scene.num-envs 4096 \
    --agent.max-iterations 300 \
    --agent.save-interval 25 \
    --agent.logger tensorboard \
    --agent.experiment-name taller_demo
```

| Opción | Qué hace |
|---|---|
| `Mjlab-StandUp-Flat-MicroDuck` | **Qué aprende** el robot. Cada tarea trae su propia recompensa. |
| `--env.scene.num-envs 4096` | Cuántos robots entrenan **a la vez**. Más robots, más experiencia por minuto. |
| `--agent.max-iterations 300` | Cuántas **rondas** de aprender. Cada ronda son miles de pasos de simulación. |
| `--agent.save-interval 25` | Guarda el cerebro **cada 25 rondas**. Son los *checkpoints*: la progresión. |
| `--agent.logger tensorboard` | Guarda la **curva de aprendizaje** en tu PC (sin cuentas externas). |
| `--agent.experiment-name` | La carpeta donde se guarda: `logs/rsl_rl/<nombre>/`. |

## Cómo leer la curva

- **`Train/mean_reward`**: puntos medios por intento. Si **sube**, el robot está aprendiendo.
- **`Train/mean_episode_length`**: cuánto aguanta antes de caerse. Cuando llega al máximo, ya no se cae.
- Un entrenamiento real del taller (levantarse del suelo, 300 rondas, ~10 min): la recompensa pasó de **0,45 a 34,6**
  y el robot pasó de caerse en 20 pasos a aguantar los 300.

## Qué se puede aprender (tareas)

| Tarea | Qué aprende |
|---|---|
| `Mjlab-Velocity-Flat-MicroDuck` | **Andar** siguiendo una orden de velocidad (la tarea principal). |
| `Mjlab-StandUp-Flat-MicroDuck` | **Levantarse** del suelo y mantenerse de pie. |
| `Mjlab-SitStand-Flat-MicroDuck` | Sentarse y levantarse suavemente. |
| `Mjlab-Roulade-Flat-MicroDuck` | Hacer una **voltereta** hacia delante. |
| `Mjlab-BallKick-Flat-MicroDuck` | **Patear** una pelota. |
| `Mjlab-Velocity-Flat-MicroDuck-Rollers` | **Patinar** con ruedas bajo los pies. |
| `Mjlab-Spin-Flat-MicroDuck` | **Girar** rápido sobre patines. |

La lista completa y actual: `cd ~/microduck_rl && uv run list-envs`.

## Del entrenamiento al simulador del taller

Durante el entrenamiento se guardan ficheros `.pt` (el cerebro en formato PyTorch, uno por checkpoint). El simulador
del taller lee `.onnx`, un formato que no necesita PyTorch ni GPU. Convertir de uno a otro se llama **exportar**, y el
entrenamiento **ya lo hace solo al terminar**: en la carpeta de la carrera queda un `.onnx`.

```bash
ls ~/microduck_rl/logs/rsl_rl/taller_taller/*/*.onnx
```

Copia ese `.onnx` a la carpeta `policies/` del repo del taller y úsalo, por ejemplo, en
`exercises/n3_00_demo_con_cerebro.py` cambiando `ANDAR = "policies/tu_cerebro.onnx"`.
(Para exportar un checkpoint intermedio hay que usar `scripts/export.py`, ver el README de microduck_rl.)

## Retomar un entrenamiento

```bash
cd ~/microduck_rl
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096 \
    --agent.run-name continuar --agent.load-checkpoint model_299.pt --agent.resume True
```

## Si algo falla

| Síntoma | Causa probable |
|---|---|
| `No veo ninguna GPU NVIDIA` | Falta el driver de NVIDIA (en Windows, WSL2 usa el driver de Windows). |
| `uv sync` se corta a medias | Conexión lenta: el script ya sube el tiempo de espera; vuelve a lanzarlo, continúa donde estaba. |
| `PyTorch no detecta CUDA` | Driver antiguo o PyTorch sin CUDA: relanza `./preparar_entrenamiento.sh`. |
| Falta memoria de la GPU | Baja `--env.scene.num-envs` a 2048 o 1024 (aprende igual, algo más lento). |

Proyecto original: <https://github.com/pollen-robotics/microduck_rl> (Apache-2.0).

## Experimentos: ¿qué pasa si cambio un parámetro?

La mejor forma de entender los parámetros es **cambiar uno y comparar curvas**. `experimentos.sh` entrena 6 veces la misma tarea
(100 rondas, misma semilla), cambiando **un solo** parámetro cada vez (~20 min en una RTX 4090):

| Experimento | Qué cambia | Qué pregunta responde |
|---|---|---|
| `base` | nada | el punto de comparación |
| `pocos_robots` | `--env.scene.num-envs 256` | ¿importa cuántos robots entrenan a la vez? |
| `lr_alto` | `--agent.algorithm.learning-rate 0.01` | ¿qué pasa con pasos de ajuste muy grandes? |
| `lr_bajo` | `--agent.algorithm.learning-rate 0.00005` | ¿y con pasos muy pequeños? |
| `exploracion` | `--agent.algorithm.entropy-coef 0.1` | ¿ayuda probar más cosas raras? |
| `miopia` | `--agent.algorithm.gamma 0.8` | ¿importa que piense a largo plazo? |

```bash
./experimentos.sh
cd ~/microduck_rl && .venv/bin/python <esta carpeta>/exportar_curvas.py logs/rsl_rl <esta carpeta>/resultados \
    base=exp_base pocos_robots=exp_pocos_robots lr_alto=exp_lr_alto lr_bajo=exp_lr_bajo exploracion=exp_exploracion miopia=exp_miopia
python exercises/n3_04_curvas_entrenamiento.py     # y compáralas
```

Hay otros parámetros que merece la pena probar: el tamaño de la red (`--agent.actor.hidden-dims 64 64`), el límite de cambio
(`--agent.algorithm.clip-param`) o el peso de cada recompensa (`--env.rewards.upright-sharp.weight 0`). **Cuidado al comparar
recompensas:** si cambias el peso de una recompensa, la puntuación deja de ser comparable con la de otro experimento.
