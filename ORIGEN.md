# De donde viene cada cosa (y licencias)

Este repositorio es **autosuficiente**: un `git clone` y `INSTALAR.bat` bastan, sin internet ni cuentas.

| Carpeta | Origen | Licencia |
|---|---|---|
| `workshop-ia-fisica/` | Copia de `david2526IA/workshop-ia-fisica` (commit `06983fb`) con el instalador adaptado y OpenCV añadido a `wheels/` | Codigo Apache-2.0 (Pollen Robotics); mallas 3D `robot/assets/` CC BY-NC-SA 4.0: **solo uso no comercial** |
| `rayuela-oficial/` | Copia sin cambios de [Bravo-Robots/microduck_rl-rayuela](https://github.com/Bravo-Robots/microduck_rl-rayuela) (commit `6c95f50`, rama `rayuela-ros2-humble`) | Apache-2.0 (ver `rayuela-oficial/LICENSE`) |
| `windows/` | Capa para Windows: lanzador, ROS 2 en miniatura (`ros_shim/`), entorno de entrenamiento y caso de la cuerda | Apache-2.0 |
| `exercises_rayuela/` | Los ejercicios nuevos del taller | Apache-2.0 |

`rayuela-oficial/` **no se modifica**: `windows/casos.py` lo ejecuta tal cual, sustituyendo solo lo que en Ubuntu hace ROS 2.
Las mallas del robot son CC BY-NC-SA: si el repositorio se hace publico, mantener esa nota.
