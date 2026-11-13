# Taller · RL en MuJoCo: del entrenamiento al despliegue de políticas para el Microduck

Taller práctico de 5 horas en **Windows, sin GPU**. Un pequeño robot bípedo, el **Microduck** (Pollen Robotics), aprende a
**jugar a la rayuela**: patear una pelota con la fuerza justa para que caiga en la casilla elegida. Todo en simulación
(MuJoCo), sin robot real y sin saber nada de IA de antemano.

## Empezar (4 pasos)

1. Crea una carpeta **vacía y corta**, fuera de OneDrive (por ejemplo `C:\taller`), ábrela con VS Code (clic derecho → *Abrir con Code*,
   o abre una terminal dentro y escribe `code .`).
2. Abre la terminal de VS Code (`Ctrl+ñ`; `Ctrl+`` en teclado inglés) y clona **dentro** de la carpeta (con el punto final):
   ```
   git clone https://github.com/david2526IA/taller_microduck_windows .
   ```
   Sin git: en GitHub, *Code → Download ZIP* y descomprime en `C:\taller`.
3. Instala: `.\INSTALAR.bat` (2-3 minutos, sin internet ni administrador). **No toques el teclado hasta que acabe.**
   Debe terminar en **TODO LISTO**.
4. Abre **[`PROGRAMA.md`](PROGRAMA.md)**: es el orden del taller, bloque a bloque, con el archivo que toca en cada momento. Si una palabra no la conoces: [`GLOSARIO.md`](GLOSARIO.md).

> En el explorador de VS Code, el doble clic **abre** el archivo para editarlo, no lo ejecuta. Los `.bat` se ejecutan desde el
> Explorador de Windows, o escribiendo `.\INSTALAR.bat` en la terminal de VS Code.

## Cómo se trabaja: un archivo, una cosa que cambiar, un efecto que ver

| Bloque | Qué cambias | Qué ves |
|---|---|---|
| 1 · El robot en el simulador | La postura, la fricción, la masa | Un pato sin IA que se cae en menos de 1 s |
| 2 · Laboratorio de mundos | Gravedad, colores, suelo, objetos, circuito de obstáculos | El mismo robot en la Luna, sobre hielo, en un laberinto |
| 3 · El cerebro y la recompensa | Sentidos, ruido, pesos de la recompensa | Qué es una política y qué necesita para decidir |
| 4 · La voltereta: de cero a experto | El checkpoint, y la recompensa y el PPO de la patada | Nueve momentos reales de un entrenamiento; entrenas tú en CPU |
| 5 · Configura tu entrenamiento real | Pesos y ajustes de un entrenamiento de verdad | Tu paquete listo para lanzar en un PC con GPU |
| 6 · ROS 2 y la partida | Tu política, el objetivo | La partida de la rayuela con **tu** política |
| 7 · Sim-to-real | Cuánto varía el mundo al entrenar | Una política que aguanta mundos que no ha visto |

**El ciclo de trabajo:** abre el archivo → cambia UN parámetro (están arriba, con comentarios que dicen en qué afecta)
→ guarda (Ctrl+S) → **cierra la ventana del robot** → `F5` y observa.

**Las diapositivas del taller** están en el repositorio: `workshop-ia-fisica/presentaciones/Presentacion_03_taller_completo.pptx` (y su `.pdf`). Cada diapositiva lleva notas del ponente.

Todos los ejercicios y sus parámetros, uno a uno: **[`PROBAR.md`](PROBAR.md)**.

**Sin editar ficheros:** `MJLAB.bat` abre `mini_mjlab`, con los mismos verbos que mjlab pero en CPU:
`MJLAB play Mini-Obstacles-MicroDuck --set NIVEL=3 --set CEREBRO=rough_walk_e` · `MJLAB list-envs` · `MJLAB params <entorno>` · `MJLAB train Mini-Kick-MicroDuck` · `MJLAB validate Mini-Obstacles-MicroDuck`.

## Qué hay aquí

```
PROGRAMA.md / GLOSARIO.md                  el orden del taller (5 h), bloque a bloque · las palabras sin jerga
INSTALAR.bat / COMPROBAR.bat               preparar el PC · comprobar que todo funciona
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
