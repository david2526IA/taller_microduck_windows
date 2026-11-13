# De donde viene cada cosa (y licencias)

Este repositorio es **autosuficiente**: un `git clone` y `INSTALAR.bat` bastan, sin internet ni cuentas.

| Carpeta | Origen | Licencia |
|---|---|---|
| `workshop-ia-fisica/` | Copia de `david2526IA/workshop-ia-fisica` (commit `06983fb`) con el instalador adaptado y OpenCV añadido a `wheels/` | Codigo Apache-2.0 (Pollen Robotics); mallas 3D `robot/assets/` CC BY-NC-SA 4.0: **solo uso no comercial** |
| `rayuela-oficial/` | Copia sin cambios de [Bravo-Robots/microduck_rl-rayuela](https://github.com/Bravo-Robots/microduck_rl-rayuela) (commit `6c95f50`, rama `rayuela-ros2-humble`) | Apache-2.0 (ver `rayuela-oficial/LICENSE`) |
| `windows/` | Capa para Windows: lanzador, ROS 2 en miniatura (`ros_shim/`), entorno de entrenamiento y caso de la cuerda | Apache-2.0 |
| `exercises_rayuela/` | Los ejercicios nuevos del taller | Apache-2.0 |
| `windows/politicas/` | `rough_walk_e` y `rough_walk_g`: [Hugging Face](https://huggingface.co/pollen-robotics) (Pollen Robotics), con su ficha `manifest.json` · `duelo2.onnx`: proyecto `patos_cuerda` (Bravo Robots) · `ejemplos/`: las tres políticas de ejemplo de `n5_01`, generadas en este repositorio con `n3_05` | Apache-2.0 |
| `workshop-ia-fisica/policies/voltereta/` | 9 checkpoints de un entrenamiento real de la voltereta (`microduck_rl`, 20.750 rondas, septiembre 2026), convertidos de `.pt` a `.onnx` con el normalizador dentro y verificados contra el export oficial de la misma carrera (diferencia máxima 0,0). Ver su `LEEME.md` | Apache-2.0 |
| `PROGRAMA.md`, `GLOSARIO.md`, `PROBAR.md` | Guía del taller, glosario y lista de ejercicios | Apache-2.0 |
| `mi_entrenamiento/` | Lo crea cada alumno al ejecutar los ejercicios `n6_*`; **no se sube** (está en `.gitignore`) | — |

`rayuela-oficial/` **no se modifica**: `windows/casos.py` lo ejecuta tal cual, sustituyendo solo lo que en Ubuntu hace ROS 2.
Las mallas del robot son CC BY-NC-SA: si el repositorio se hace publico, mantener esa nota.

## Pendiente de confirmar antes de difundir
- **Imágenes y vídeos de las diapositivas.** Las fotos y el vídeo del robot real vienen del material de prensa de Pollen Robotics (créditos en la diapositiva final). Conviene confirmar que su licencia permite reutilizarlos en una presentación pública.
- **Licencia del repositorio.** El código propio se indica como Apache-2.0, pero el repositorio no incluye todavía un fichero `LICENSE` en la raíz.
- **Datos medidos.** Todos los números del taller (voltereta, patada, circuito, sim-to-real) son de simulación en este PC, con pocas semillas: orientativos. Nada se ha probado con el robot real.
