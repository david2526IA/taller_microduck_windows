# Si llevas Ubuntu (y, opcionalmente, una GPU NVIDIA)

El taller está pensado para **Windows sin GPU** (`INSTALAR.bat`, `MJLAB.bat`). Si llevas **Ubuntu 22.04**, tienes dos caminos que ya existen en este repositorio.
Importante: ninguno de los dos se ha probado en esta máquina (es Windows); vienen del trabajo de Bravo Robots en Linux y de sus instrucciones oficiales.

## 1 · Los ejercicios del taller (sin GPU)
Los ejercicios de `workshop-ia-fisica/exercises/` (n1 a n3) funcionan en Linux: crea el entorno con Python 3.12 e instala las librerías de `workshop-ia-fisica/wheels/` (son para Windows) o de PyPI:
```bash
cd workshop-ia-fisica
python3.12 -m venv .venv
.venv/bin/pip install mujoco==3.17.0 onnxruntime==1.31.1 numpy==2.5.4 colorama opencv-python==5.0.0.93 ./wheels/better_actuator_models-1.0.1-py3-none-any.whl
.venv/bin/python check_setup.py --viewer
```
Los ejercicios nuevos de `exercises_rayuela/` y `windows/` usan `msvcrt` (teclado de Windows): en Ubuntu no funcionan tal cual. En Ubuntu usa la versión oficial de la Rayuela (siguiente punto).

## 2 · La Rayuela oficial con ROS 2 real (`rayuela-oficial/`)
Es el repositorio oficial de Bravo Robots, **sin modificar**, con ROS 2 Humble de verdad (nodos, topics y `ros2 launch`). Sigue su `README.md` (apartado Setup):
```bash
cd rayuela-oficial
unset PYTHONPATH && uv sync                       # entorno Python 3.12 (terminal A)
source /opt/ros/humble/setup.bash                 # ROS 2 Humble (terminal B)
cd ros2_microduck && colcon build --symlink-install && source install/setup.bash
ros2 launch rayuela rayuela.launch.py use_viewer:=true
ros2 run rayuela teleop_keyboard                  # en otra terminal con ROS cargado
```
Mantén las dos terminales separadas (no actives el venv en la de ROS ni cargues ROS en la del venv): lo explica el README oficial.

## 3 · Entrenar de verdad (con GPU NVIDIA)
En `workshop-ia-fisica/entrenar/` están los scripts que usó el ponente: `preparar_entrenamiento.sh` (instala `microduck_rl` y mjlab y comprueba la GPU), `entrenar.sh` (un entrenamiento corto, ~10 min en una RTX 4090), `experimentos.sh` (6 experimentos de parámetros) y `ver_curva.sh`. Léelos con `ENTRENAR.md`.
Sirve Linux o Windows con WSL2 y una GPU NVIDIA. Sin GPU no se puede entrenar con mjlab: usa `MJLAB.bat train Mini-Kick-MicroDuck` (Windows) o `n3_05_entrena_la_patada.py`, que entrena un PPO pequeño en CPU.

## Lo que NO hay
- Una versión Ubuntu de los ejercicios nuevos (circuito de obstáculos, duelo de la cuerda, equilibrio, sim-to-real): están escritos para Windows. La lógica de simulación es de MuJoCo y se podría portar quitando el teclado de `msvcrt`.
- Instrucciones probadas para WSL2 con GPU.
