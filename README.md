# Taller · RL en MuJoCo: del entrenamiento al despliegue de políticas para el Microduck

Taller práctico de 5 horas en **Windows, sin GPU**. Un pequeño robot bípedo, el **Microduck** (Pollen Robotics), **aprende habilidades por ensayo y error**
(aprendizaje por refuerzo, RL): una **voltereta**, patear una pelota con la fuerza justa para **jugar a la rayuela**, andar por un circuito de obstáculos...
Todo en simulación (MuJoCo), sin robot real y sin saber nada de IA de antemano.

**Qué te llevas:** entiendes el camino completo (*modelar el robot → crear el entorno → entrenar → desplegar*), has cambiado mundos, recompensas y botones de
entrenamiento viendo qué pasa, has entrenado un PPO de verdad en tu CPU, y sales con **tu propio paquete de entrenamiento listo para lanzar** en un PC con GPU o en la nube.

## Empezar (4 pasos)

1. Crea una carpeta **vacía y corta**, fuera de OneDrive (por ejemplo `C:\taller`), ábrela con VS Code (clic derecho → *Abrir con Code*,
   o abre una terminal dentro y escribe `code .`).
2. Abre la terminal de VS Code (`Ctrl+ñ`; `Ctrl+`` en teclado inglés) y clona **dentro** de la carpeta (con el punto final):
   ```
   git clone --depth 1 https://github.com/david2526IA/taller_microduck_windows .
   ```
   El `--depth 1` descarga solo la última versión (la mitad de peso): **imprescindible con wifi justo**. Sin él, el historial completo (~160 MB) puede cortarse a mitad de la descarga («early EOF»); si te pasa, vuelve a clonar con `--depth 1`.
   Sin git: en GitHub, *Code → Download ZIP* y descomprime en `C:\taller`.
3. Instala: `.\INSTALAR.bat` (2-3 minutos, sin internet ni administrador). **No toques el teclado hasta que acabe.**
   Debe terminar en **TODO LISTO**.
4. Abre **[`PROGRAMA.md`](PROGRAMA.md)**: es el orden del taller, bloque a bloque, con el archivo que toca en cada momento. Si una palabra no la conoces: [`GLOSARIO.md`](GLOSARIO.md).

> En el explorador de VS Code, el doble clic **abre** el archivo para editarlo, no lo ejecuta. Los `.bat` se ejecutan desde el
> Explorador de Windows, o escribiendo `.\INSTALAR.bat` en la terminal de VS Code.

## Qué necesitas
- **Windows 10 u 11** de 64 bits, **sin GPU**, con unos 4 GB libres. **Python 3.12**, **Git** y **VS Code** (los instala informática; `INSTALAR.bat` lo comprueba).
- Drivers gráficos al día (el visor 3D usa OpenGL 3.3 o superior). Una carpeta **corta y fuera de OneDrive**, por ejemplo `C:\taller`.
- Internet solo para el `git clone`; después, nada.
- No hace falta saber programar: en cada ejercicio solo cambias números y lees lo que pasa.

## Cómo se trabaja: un archivo, una cosa que cambiar, un efecto que ver

| Bloque | Qué cambias | Qué ves |
|---|---|---|
| **1 · Modelar** (el robot y su mundo) | La postura, la fricción, la masa; gravedad, colores, objetos, circuito de obstáculos | Un pato sin IA que se cae en menos de 1 s; el mismo robot en la Luna, sobre hielo, en un laberinto |
| **2 · El entorno y el RL** | Sentidos, ruido, pesos de la recompensa | Qué es una política y qué necesita para decidir |
| **3 · Entrenar** | El checkpoint; la recompensa y el PPO de la patada; los pesos de un entrenamiento real | Nueve momentos reales de un entrenamiento; entrenas tú en CPU; tu paquete listo para una GPU |
| **4 · Desplegar** | Tu política, el objetivo; cuánto varía el mundo al entrenar | La partida de la rayuela con **tu** política; una política que aguanta mundos que no ha visto |

**El camino esencial:** hay más ejercicios de los que caben en 5 horas. En [`PROGRAMA.md`](PROGRAMA.md) están marcados con ⭐ los **12 imprescindibles**; el resto (➕) es para quien vaya sobrado o para casa.
**Tu cuaderno:** [`CUADERNO.md`](CUADERNO.md) es una página para **predecir antes de cambiar** y apuntar lo que aprendes.

**El ciclo de trabajo:** abre el archivo → cambia UN parámetro (están arriba, con comentarios que dicen en qué afecta)
→ guarda (Ctrl+S) → **cierra la ventana del robot** → `F5` y observa.

**Las diapositivas del taller** están en el repositorio: `workshop-ia-fisica/presentaciones/Presentacion_03_taller_completo.pptx` (y su `.pdf`). Cada diapositiva lleva notas del ponente.

Todos los ejercicios y sus parámetros, uno a uno: **[`PROBAR.md`](PROBAR.md)**.

**Sin editar ficheros:** `MJLAB.bat` abre `mini_mjlab`, con los mismos verbos que mjlab pero en CPU:
`MJLAB play Mini-Obstacles-MicroDuck --set NIVEL=3 --set CEREBRO=rough_walk_e` · `MJLAB list-envs` · `MJLAB params <entorno>` · `MJLAB train Mini-Kick-MicroDuck` · `MJLAB validate Mini-Obstacles-MicroDuck`.

## Qué hay aquí

```
PROGRAMA.md / CUADERNO.md / GLOSARIO.md    el orden del taller (5 h) y sus 12 ejercicios esenciales · tu cuaderno · las palabras sin jerga
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
