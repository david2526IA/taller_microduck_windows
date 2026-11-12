# TALLER · IA aplicada a un entorno físico

Esta es tu hoja de ruta. Sigue los bloques **en orden**. En cada uno encontrarás:
**🎯 Aprenderás** (la idea) · **🛠 Haz** (los pasos) · **👀 Observa** (qué mirar) · **💭 Piensa** (para fijar la idea).

- **Nivel 1** = ejecutar y mirar. **Nivel 2** = cambiar 3-4 valores y ver qué pasa. Si terminas el Nivel 1, pasa al 2: nadie se queda parado.
- Todos los comandos se escriben en la **terminal de VS Code** (`Terminal → New Terminal`), con esta carpeta abierta. También puedes abrir un ejercicio y pulsar **F5**.
- Las teclas de los programas con robot se pulsan **en la terminal**, no en la ventana del robot. **Q** cierra.
- Las palabras técnicas están en el [glosario](#glosario) del final.

| Hora | Bloque | Duración |
|---|---|---|
| 0:00 | **Lo primero: prepara tu PC** (clonar e instalar, en segundo plano) | 8 min |
| 0:08 | Ignición: la IA sale de la pantalla | 12 min |
| 0:20 | **1 · Despliega tu laboratorio**: el repositorio, las carpetas y cómo trabajar | 60 min |
| 1:20 | **2 · Del plano al gemelo digital** | 30 min |
| 1:50 | **3 · El cerebro**: cómo aprende una IA física | 55 min |
| 2:45 | Descanso | 10 min |
| 2:55 | **4 · Laboratorio: pon a prueba al robot** | 90 min |
| 4:25 | **5 · Del gemelo digital a la realidad** | 20 min |
| 4:45 | Cierre y próxima misión | 15 min |

---

## Lo primero de todo: prepara tu PC (8 minutos, al empezar)

Lo haces **nada más empezar la charla**: sin el repositorio no puedes interactuar con nada. La instalación sigue sola en segundo plano mientras el ponente empieza la Ignición. Cuando acabe, ejecuta tú mismo `exercises/n2_02_sin_cerebro.py` y mira cómo se cae el robot.

1. Crea una carpeta, ábrela en VS Code (o abre una terminal en ella y escribe `code .`).
2. En la terminal: `git clone <dirección del repositorio que te dice el ponente> .`
3. Haz **doble clic en `INSTALAR.bat`**. Instala solo lo necesario, sin internet, y sigue en segundo plano mientras empieza la Ignición.
4. Cuando acabe, doble clic en `COMPROBAR.bat` (o `python check_setup.py --viewer`): debe acabar en **TODO LISTO**.

---

## Bloque 1 · Despliega tu laboratorio (60 min)

🎯 **Aprenderás** a moverte por un proyecto técnico: qué hay en cada carpeta, cómo se lanza y se modifica un ejercicio, y cómo comprobar que todo funciona. Todo lo que viene después parte de aquí.

| Carpeta / fichero | Qué es | ¿Lo tocas? |
|---|---|---|
| `robot/` | el **cuerpo** (`robot_groundcontact.xml`) y el **mundo** (`scene.xml`) | solo `scene.xml` |
| `policies/` | el **cerebro**: redes ya entrenadas (`.onnx`) | no, se copian |
| `exercises/` | tus ejercicios: `n1` mirar, `n2` cambiar valores, `n3` laboratorio | sí: las constantes de arriba |
| `scripts/` | el programa que une cuerpo y cerebro (`infer_policy.py`) | no |
| `entrenar/` | cómo entrenar en casa: scripts y curvas reales | se lee |
| `check_setup.py` | comprueba que todo funciona | se ejecuta |

**El ciclo de trabajo de todo el taller** (el fallo más típico es olvidar el paso 3):
1. **Abre** el ejercicio en VS Code: arriba hay unas constantes en mayúsculas.
2. **Cambia UN valor** (y antes, *predice* qué pasará).
3. **Guarda** (Ctrl+S) y **cierra la ventana del robot**: no se recarga sola.
4. **Lanza** otra vez y observa. ¿Acertaste?

🛠 **Comprueba tu laboratorio:** `python check_setup.py --viewer` → debe acabar en **TODO LISTO** y abrir el robot 5 segundos.
🛠 **Practica el ciclo:** abre `exercises/n1_01_ver_pieza.py`, cambia `PIEZA = "leg"` por `"foot_left"`, guarda, cierra y lanza. Es una pieza suelta del robot (una malla de triángulos); no hace falta entender nada más.
🛠 Abre `check_setup.py` y busca qué comprueba cada línea.
💭 **Piensa:** ¿qué dos cosas necesita un robot para moverse en un simulador? (cuerpo y cerebro). ¿Dónde está cada una en las carpetas?

---

## Bloque 2 · Del plano al gemelo digital (30 min)

🎯 **Aprenderás** cómo se convierte un robot real en un modelo que un simulador puede mover: piezas 3D → masas y motores → mundo.

| Etapa | Fichero (carpeta `robot/`) | Qué es |
|---|---|---|
| 1 · Piezas | `assets/*.stl` | las piezas en 3D |
| 2-3 · El robot | `robot_groundcontact.xml` | masas, colisiones, motores (formato MJCF) |
| 4 · El mundo | `scene.xml` | suelo, luz, posturas guardadas |
| 5 · Validación | `exercises/n1_00_ver_robot.py` | comprobar que se tiene en pie |

🛠 **Etapa 1:** `python exercises/n1_01_ver_pieza.py`. Cambia `PIEZA` por otra de `robot/assets/` (`foot_left`, `leg`, `top_head_shell`…).
🛠 **Etapa 5 (Nivel 1):** `python exercises/n1_00_ver_robot.py`. Cambia `POSE = "STAND"` por `"SIT"` o `"FOLD"`.
🛠 **Nivel 2:** en `robot/scene.xml` busca `groundplane` y cambia `rgb1`/`rgb2` (colores del suelo). Guarda y vuelve a ejecutar.
👀 **Observa:** con ratón izquierdo giras, derecho mueves, rueda = zoom. **Ctrl + clic derecho** arrastrando sobre el robot lo empuja.

💭 **Piensa:** ¿qué cosas del robot real NO están en este modelo? (Pista: la holgura de los engranajes, la batería, los retrasos…)

---

## Bloque 3 · El cerebro: cómo aprende una IA física (55 min)

🎯 **Aprenderás** que el cerebro de un robot es una **función** (le entran números, le salen órdenes), que sus «botones» (pesos) se ajustan aprendiendo, y que lo que aprende depende de la **recompensa** con que se puntúa.

**Nivel 1 — Playground (navegador, opcional):** <https://playground.tensorflow.org>
🛠 Añade neuronas, cambia el *learning rate* y mira cómo la red aprende a separar los puntos.

**Nivel 2 — el cerebro del pato, por dentro y en vivo:** `python exercises/n2_00_cerebro_en_vivo.py`
🛠 Anda con las flechas **en la terminal** y empuja al pato con **Ctrl + clic derecho**.
👀 **Observa:** a la izquierda de la terminal entran **61 números** (giro, inclinación, posición y velocidad de los motores…) y salen **14 órdenes**, una por motor, 50 veces por segundo.
🛠 **Pruébalo estropeado** (cambia una constante de arriba, guarda y relanza):
- `QUITAR_SENTIDO = "inclinacion"` → ¿qué pasa si el pato no sabe hacia dónde cae? Prueba también `"giro"`, `"posicion"`, `"velocidad"` y `"ultima_orden"`.
- `RUIDO_SENTIDOS = 0.05`, `0.2`, `0.5` → sentidos «borrosos».
- `RUIDO_ORDENES = 0.1`, `0.3`, `0.6` → motores «temblorosos».

💭 **Piensa:** ¿a qué sentidos hace más caso el pato? ¿Por qué un cerebro entrenado para unas condiciones aguanta poco ruido?

**Nivel 2 — la recompensa, en vivo:** `python exercises/n2_01_recompensa_en_vivo.py`
🛠 Anda y empuja al pato.
👀 **Observa:** cada paso se puntúa con una **suma de piezas × pesos**: altura del tronco, verticalidad, avanzar y esfuerzo de los motores. ¿Qué piezas bajan cuando casi se cae?
🛠 **Cambia los pesos** (`PESO_ALTURA`, `PESO_VERTICAL`, `PESO_AVANZAR`, `PESO_ESFUERZO`), guarda y relanza:
- Pon `PESO_AVANZAR = 5` y los demás en `0`: solo premias avanzar. Empuja al pato hacia delante y mira la nota mientras se cae.

💭 **Piensa:** si solo recibe puntos por avanzar, ¿qué truco raro podría aprender? ¿Por qué diseñar la recompensa es la parte difícil?
✅ Si lo respondes, has entendido el aprendizaje por refuerzo.

**Nivel 2 — entra en la red:** `python exercises/n2_03_dentro_del_cerebro.py`
🎯 El cerebro es un fichero con **197.896 números** (pesos). Aquí haces TÚ la misma cuenta que hace `onnxruntime`, capa a capa: 61 entradas → normalizar → 512 → 256 → 128 → 14 órdenes.
👀 **Observa:** cuántas neuronas hay activas en cada capa y cómo cambia la actividad cuando empujas al pato.
🛠 **Pruébalo** (cambia una constante, guarda, cierra la ventana y relanza):
- `CEREBRO = "progresion_0_recien_nacido"` y después `"progresion_4_mejor"`: la misma red con otros pesos.
- `APAGAR_CAPA1 = 0.5`, `0.9`, `0.99` y `1.0`: apagas neuronas de la primera capa. Predice cuándo se cae.
💭 **Piensa:** aguanta con el 99 % de la primera capa apagada y solo cae al apagarla toda. ¿Qué dice eso de cómo reparte el trabajo una red entrenada?

---

## Bloque 4 · Laboratorio: pon a prueba al robot (90 min)

🎯 **Aprenderás** qué hace un cerebro que una postura fija no hace, y por qué un robot entrenado en simulador es frágil cuando cambia el mundo.

### A · Verlo actuar (10 min)
- Windows: doble clic en `run_demo.bat`. Linux/Mac: `python exercises/n3_00_demo_con_cerebro.py`.
- Teclas: ↑ ↓ velocidad · ← → lado · `A`/`E` girar · `Y` sentarse · `R` voltereta · Espacio parar.
- **Ctrl + clic derecho** en el visor para empujarlo.

**Contraste — el robot SIN cerebro:** `python exercises/n2_02_sin_cerebro.py`
👀 Se cae en menos de un segundo. Prueba otra `FRICCIONES` o `FACTOR_MASA`: ¿algo lo salva?
💭 **Piensa:** ¿qué hace el cerebro que no hace una postura fija? (reacciona 50 veces por segundo)

### B · Cambiar el mundo (20 min)
Añade estas opciones al final del comando de la demo:

| Opción | Qué simula |
|---|---|
| `--vin 6.5` | batería baja |
| `--delay 2 4` | retraso en los motores |
| `--action-scale 0.7` | motores menos potentes |
| `--walking policies/otro.onnx` | otro cerebro |

Ejemplo: `run_demo.bat --vin 6.5 --delay 2 4`
**Suelo resbaladizo (Nivel 2):** en `robot/scene.xml` busca la línea del suelo `floor` y cambia `friction="1 …"`: prueba `0.1` (hielo) y `2` (goma). **Déjalo otra vez en `1` al terminar.**

### C · Comparar cerebros (10 min)
`python exercises/n3_01_progresion.py` y cambia `NIVEL` de 0 a 5: es el **mismo** robot con el **mismo** entrenamiento guardado en momentos distintos.
👀 ¿Cuándo empieza a andar? ¿Cuándo aguanta un empujón?

### D · Entrenar un cerebro (25 min)
Hasta ahora usaste cerebros **ya entrenados**. Aquí ves cómo se entrena uno, con datos reales de un entrenamiento ya hecho. No se entrena nada hoy: no hace falta GPU.

**El ciclo de entrenamiento** (se repite cientos de veces):

| Paso | Qué ocurre | Parámetro que lo controla |
|---|---|---|
| 1 · Elegir la **tarea** | Qué debe aprender (levantarse, andar, patinar…) y qué se premia | el nombre de la tarea y sus `rewards` |
| 2 · **Jugar** | 4096 robots simulados prueban el cerebro actual durante 24 pasos | `--env.scene.num-envs`, `num-steps-per-env` |
| 3 · **Puntuar** | Cada intento recibe una recompensa | `--env.rewards.*.weight` |
| 4 · **Ajustar** | El algoritmo (PPO) mueve los botones hacia lo que dio más puntos | `learning-rate`, `gamma`, `entropy-coef`, `clip` |
| 5 · **Guardar** | Cada N rondas se guarda una copia (checkpoint) | `--agent.save-interval` |
| 6 · **Repetir** | Hasta acabar las rondas | `--agent.max-iterations` |

**Los parámetros que importan** (valores del Microduck):

| Parámetro | Valor | Qué controla | Si lo subes… |
|---|---|---|---|
| `num-envs` | 4096 | robots a la vez | aprende antes (más experiencia por ronda), necesita más GPU |
| `learning-rate` | 0,001 | tamaño de cada ajuste | muy alto: se descontrola · muy bajo: casi no avanza |
| `entropy-coef` | 0,01 | premio por probar cosas distintas | demasiado alto: nunca se decide y la recompensa se hunde |
| `gamma` | 0,99 | cuánto importa el futuro | más bajo: solo piensa en lo inmediato |
| `clip` | 0,2 | límite de cuánto cambia el cerebro en un ajuste | evita que un mal ajuste estropee lo aprendido |
| `hidden-dims` | 512, 256, 128 | tamaño de la red | más grande: más capacidad, más lento |
| `max-iterations` | 300 (demo) | rondas de entrenamiento | más rondas, mejor cerebro (hasta que se estanca) |

**Tu parte:** abre `python exercises/n3_04_curvas_entrenamiento.py`. Son curvas **reales** de entrenar el mismo robot cambiando un parámetro cada vez. **Primero apunta tu predicción** (en `MISIONES.md`, misiones 12-15) y **después** marca la casilla.
Para entenderlo con calma: [`entrenar/ENTRENAR.md`](entrenar/ENTRENAR.md).

### E · La configuración de un entrenamiento + misiones (25 min)
**La configuración (técnico, 10 min).** El ponente enseña los valores reales de un entrenamiento y cómo se cambian:
- Dos ficheros lo guardan todo: `params/env.yaml` (el entorno: 4096 robots, 50 Hz, episodios de 6 s) y `params/agent.yaml` (el algoritmo PPO y la red de 512-256-128).
- **La recompensa es una suma con pesos.** Cada pieza se multiplica por su peso (por ejemplo `upright_sharp` +1,5 premia estar vertical y `action_rate_l2` −0,1 castiga sacudir los motores). Es lo que más cambia lo que aprende el robot.
- Cualquier valor se cambia al lanzar: `--agent.algorithm.learning-rate 0.0005`, `--env.scene.num-envs 2048`, `--env.rewards.upright-sharp.weight 0`.

**Misiones a tu ritmo (15 min).** Sigue con [`MISIONES.md`](MISIONES.md): 16 misiones cortas con casillas para anotar lo que observas. Si terminas, prueba los patines:
> 🛼 **Extra visual:** `python exercises/n3_03_patinar.py`: el mismo robot con patines y otro cerebro.

> 🏆 **Opcional, para quien vaya sobrado — reto «haz que falle / haz que gane»** (hoja en [`PUNTUACION_RETO.md`](PUNTUACION_RETO.md)): con `python exercises/n3_02_marcador.py` cuenta los segundos de pie y tus empujones (Ctrl + clic derecho) y da los **PUNTOS** (segundos de pie, máx. 60, menos empujones). Cambia `VOLTAJE_BATERIA`, `RETRASO_MOTORES`, `POTENCIA_MOTORES` o `ROZAMIENTO_PIES` para endurecer la ronda. Cierra con `Q` para repetir.

**Graba tu mejor momento:** `Win + Alt + R` (Xbox Game Bar).

---

## Bloque 5 · Del gemelo digital a la realidad (20 min)

🎯 **Aprenderás** por qué lo difícil no es entrenar en el simulador, sino que funcione fuera.

Cada opción que has tocado representa un problema real:

| Lo que cambiaste | Qué pasa en el robot real |
|---|---|
| `--vin` | la batería se agota y el motor empuja menos |
| `--delay` | las órdenes llegan unos milisegundos tarde |
| `--action-scale` | los motores no rinden igual |
| fricción de `scene.xml` | el suelo de verdad no es el del simulador |

La receta contra esa brecha se llama **domain randomization**: entrenar con el mundo cambiando al azar para que el cerebro no dependa de un valor exacto.

💭 **Piensa:** ¿qué cambiarías en el entrenamiento para que el robot aguante batería baja?

**¿Y cómo se entrena un cerebro?** Hace falta una GPU NVIDIA, así que no se hace hoy, pero está todo explicado en [`entrenar/ENTRENAR.md`](entrenar/ENTRENAR.md), con scripts que preparan el entorno y lanzan un entrenamiento de ~10 minutos.

---

## Si algo falla

| Problema | Solución |
|---|---|
| `python` no se reconoce | usa `.\.venv\Scripts\python.exe` en su lugar |
| El visor sale negro | actualiza los drivers gráficos |
| Las teclas no responden | pulsa **dentro de la terminal**, no en el visor |
| `[FALLA]` en `check_setup` | avisa al ponente |
| El robot resbala como en hielo | `robot/scene.xml`: pon el suelo `friction="1 …"` |

---

## Glosario

| Palabra | Qué significa |
|---|---|
| **Red neuronal** | Una función con muchos «botones» (pesos) que se ajustan hasta dar buenas respuestas. |
| **Política** | El cerebro del robot: recibe lo que siente y devuelve qué hacer con los motores. Aquí es un fichero `.onnx`. |
| **Aprendizaje por refuerzo** | Aprender probando cosas y recibiendo una **recompensa** (puntos) cuando sale bien. |
| **Recompensa** | La puntuación que dice si lo que hizo el robot estuvo bien o mal. |
| **Episodio** | Un intento completo, desde que empieza hasta que se cae o se acaba el tiempo. |
| **Simulador / gemelo digital** | Una copia virtual del robot en un mundo con física, donde equivocarse es gratis. |
| **MuJoCo** | El simulador de física que usamos. |
| **MJCF** | El formato de fichero que describe el robot y el mundo para MuJoCo. |
| **ONNX** | Formato de fichero para guardar una red neuronal y ejecutarla en cualquier sitio, sin GPU. |
| **PPO** | El algoritmo de aprendizaje por refuerzo con el que se entrena el Microduck. |
| **Learning rate** | Cuánto se mueven los botones de la red en cada ajuste. Muy alto, se descontrola; muy bajo, casi no avanza. |
| **Exploración (entropía)** | Cuánto prueba cosas distintas el robot en vez de repetir lo que ya sabe. Alta al principio, baja al final. |
| **Gamma** | Cuánto le importa el futuro frente a lo inmediato. Con 0,99 piensa a largo plazo. |
| **Checkpoint** | Una copia del cerebro guardada durante el entrenamiento: permite ver la progresión. |
| **Sim-to-real** | Pasar de lo que funciona en simulación a lo que funciona en el robot real. |
| **Fricción** | Cuánto agarra el suelo: 0,1 es hielo, 1 es normal, 2 es goma. |
| **Backlash** | La holgura de los engranajes de un motor pequeño; el simulador ideal no la tiene. |
