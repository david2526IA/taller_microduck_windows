# Taller · RL en MuJoCo: del entrenamiento al despliegue de políticas para el Microduck

Taller práctico de 5 horas en **Windows, sin GPU**. Un pequeño robot bípedo, el **Microduck** (Pollen Robotics), aprende a
**jugar a la rayuela**: patear una pelota con la fuerza justa para que caiga en la casilla elegida. Todo en simulación
(MuJoCo), sin robot real y sin saber nada de IA de antemano.

## Empezar (3 pasos)

1. Clona este repositorio en una carpeta **corta** (por ejemplo `C:\taller`) y ábrela en VS Code:
   ```
   git clone https://github.com/david2526IA/taller_microduck_windows C:\taller
   code C:\taller
   ```
2. Doble clic en **`INSTALAR.bat`** (2-3 minutos, sin internet ni administrador). **No toques el teclado hasta que acabe.**
   Debe terminar en **TODO LISTO**.
3. Doble clic en **`RUTA.bat`**: la ruta guiada te lleva paso a paso.

> En el explorador de VS Code, el doble clic **abre** el archivo para editarlo, no lo ejecuta. Para ejecutar un `.bat`,
> hazlo desde el Explorador de Windows o escribe `.\INSTALAR.bat` en la terminal de VS Code.

## La ruta guiada (`RUTA.bat`)

| Paso | Qué ves | Qué se aprende |
|---|---|---|
| 1 · Tu entorno | `TODO LISTO` y el robot en el visor | Entorno virtual, versiones fijas, MuJoCo |
| 2 · El pato sin cerebro | Se cae en menos de 1 s | Equilibrar no se resuelve con una postura fija |
| 3 · Meterle IA | Anda, se sienta, rueda, se recupera de empujones | El cerebro es una función: sentidos → órdenes |
| 4 · Dentro del cerebro | 61 entradas y 14 salidas en vivo | Observación → cerebro → acción |
| 5 · Cómo se le puntúa | La recompensa como suma de piezas × pesos | Diseñar la recompensa es lo difícil |
| 6 · Entrenar | PPO de verdad, ~3 min: de ~1 a ~8 aciertos de 9 | El bucle completo del RL |
| 7 · El resultado | La partida de la rayuela con **tu** política | Simulación + cerebro + visión + control |
| 8 · Sim-to-real | Contrato del .onnx y robustez en crescendo (`n5_00`) | Cómo se prepara una política antes del robot real |
| Casos de uso | Patines · duelo de la cuerda · equilibrio · ROS 2 en vivo · tu propia escena | Lo mismo con otros cuerpos y otros mundos |

**El ciclo de trabajo de todo el taller:** abre el ejercicio → cambia UN parámetro (están arriba, con comentarios que dicen en qué
afecta) → guarda (Ctrl+S) → **cierra la ventana del robot** → lánzalo otra vez y observa.

**Las diapositivas del taller** están en el repositorio: `workshop-ia-fisica/presentaciones/Presentacion_03_taller_completo.pptx` (y su `.pdf`). Cada diapositiva lleva notas del ponente.

Todos los ejercicios y sus parámetros, uno a uno: **[`PROBAR.md`](PROBAR.md)**.

**Sin editar ficheros:** `MJLAB.bat` abre `mini_mjlab`, con los mismos verbos que mjlab pero en CPU:
`MJLAB play Mini-Obstacles-MicroDuck --set NIVEL=3 --set CEREBRO=rough_walk_e` · `MJLAB list-envs` · `MJLAB params <entorno>` · `MJLAB train Mini-Kick-MicroDuck` · `MJLAB validate Mini-Obstacles-MicroDuck`.

## Qué hay aquí

```
INSTALAR.bat / COMPROBAR.bat / RUTA.bat   doble clic: preparar el PC · comprobarlo · la ruta guiada
MJLAB.bat (mini_mjlab.py)                  los verbos de mjlab (list-envs, params, play, train, validate) en CPU, con --set
exercises_rayuela/    los ejercicios del taller (n0 ... n4), con parametros editables
workshop-ia-fisica/   el proyecto base: robot, cerebros (.onnx), ejercicios n1-n3, librerias offline (wheels/), entrenar/
workshop-ia-fisica/presentaciones/   LAS PRESENTACIONES: Presentacion_03_taller_completo (.pptx y .pdf) es la del taller; la 01 y la 02 son las anteriores
rayuela-oficial/      la Rayuela oficial de Bravo Robots (sin modificar)
windows/              la capa para Windows: lanzador, ROS 2 en miniatura, entorno de entrenamiento, cuerda
```

La Rayuela oficial pide Ubuntu y ROS 2. Aquí se ejecuta **el mismo código oficial** (simulación, cerebros, visión y control)
con un ROS 2 en miniatura dentro de un proceso (`windows/ros_shim/`). No es ROS 2 real: sirve para entender nodos y topics.

## Si algo falla

| Síntoma | Qué hacer |
|---|---|
| `INSTALAR.bat` acaba sin TODO LISTO | Envía `instalar_log.txt` al ponente |
| `Filename too long` al clonar | `git config --global core.longpaths true` y clona en una ruta corta |
| La ventana del robot no se abre / negra | Actualiza los drivers gráficos; en `COMPROBAR.bat` mira si falla algo antes |
| Las teclas no hacen nada | Las teclas se pulsan en la **terminal**, no en la ventana del robot |
| Una carpeta en OneDrive va lenta | Clona fuera de OneDrive (p. ej. `C:\taller`) |

Origen y licencias: [`ORIGEN.md`](ORIGEN.md). Las mallas 3D del robot son CC BY-NC-SA 4.0: solo uso no comercial.
