# Programa del taller · 5 horas (15:00-20:00)

## La idea del taller en una frase
Un robot pequeño (el Microduck) **aprende una habilidad por ensayo y error**. Recorremos el camino completo, con las manos en el código:

```
  MODELAR el robot  →  crear el ENTORNO  →  ENTRENAR (RL)  →  DESPLEGAR (sim-to-real)
        └────────────────── y vuelta atrás: casi nunca sale a la primera ──────────────────┘
```

Cada bloque es una parte de ese camino. **Entender cada etapa** importa porque, cuando algo falla, sabes cuál tocar.

## Cómo se trabaja (siempre igual)
1. El ponente plantea **una pregunta** y explica una idea (2-5 minutos).
2. Tú abres **un archivo**: arriba están los parámetros, y cada uno dice en qué afecta.
3. Cambias **UN número**, guardas (`Ctrl+S`), **cierras la ventana del robot** si hay, y ejecutas otra vez con `F5`.
4. Miras qué ha cambiado, y lo comentamos.

Los archivos están en dos carpetas: `workshop-ia-fisica/exercises/` (la serie base, `n1` a `n3`) y `exercises_rayuela/` (el resto).
Las diapositivas: `workshop-ia-fisica/presentaciones/Presentacion_03_taller_completo.pptx` (y `.pdf`). Si una palabra no la conoces: [`GLOSARIO.md`](GLOSARIO.md).

## Los 14 ejercicios esenciales
Hay más ejercicios de los que caben en cinco horas. En cada bloque están marcados como **Esencial** los que cubren los cuatro puntos de la descripción oficial (MuJoCo y escenas propias, RL y PPO, recompensa y entrenamiento corto, ROS 2 y ONNX jugando a la rayuela). Los marcados como **Extra** son para quien avance más rápido o para hacer en casa.

| # | Bloque | Ejercicio esencial | Te llevas |
|---|---|---|---|
| 1 | 1.1 Modelar el robot | `n1_03` el despiece (y leer el XML) | De qué piezas está hecho el pato y cómo se montan en un árbol |
| 2 | 1.1 Modelar el robot | `n1_04` el robot y la escena por dentro | Los 14 motores y las articulaciones sobre el robot; qué hay escrito en el XML |
| 3 | 1.1 Modelar el robot | `n0_00` el pato sin cerebro | Sin cerebro se cae en menos de 1 s, y ni la fricción ni la masa lo salvan |
| 4 | 1.2 El mundo | `n1_02` laboratorio de mundos | El mundo es parte del problema: Luna, hielo, objetos |
| 5 | 2 Entorno y RL | `n3_00` con cerebro | El mismo robot con IA anda y se recupera de empujones |
| 6 | 2 Entorno y RL | `n2_03` dentro del cerebro | Una política es una función: 61 números entran, 14 salen |
| 7 | 2 Entorno y RL | `n2_01` la recompensa en vivo | La recompensa es una nota: suma de piezas × pesos |
| 8 | 3.1 Entrenar | `n3_07` voltereta, checkpoint a checkpoint | Un entrenamiento tiene fases: no sabe, aparece, se vuelve irregular, se estabiliza |
| 9 | 3.1 Entrenar | `n3_08` medir la voltereta | Se mide y se elige: el último checkpoint no siempre es el mejor |
| 10 | 3.1 Entrenar | `n3_05` entrena la patada (PPO, ~3 min) | Entrenas tú, de verdad, en tu CPU |
| 11 | 3.2 Configurarlo | `n6_00` configura tu entrenamiento real | Tu paquete listo para una GPU; sabes qué botón tocar |
| 12 | 4.1 Desplegar | `n4_01` ROS 2 en vivo | Nodos y topics: cómo se conectan visión, control y teleoperación |
| 13 | 4.1 Desplegar | `n4_00` la partida de la rayuela | Tu política jugando con visión, control y marcador |
| 14 | 4.2 Sim-to-real | `n5_01` generalizar | Aleatorizar no basta: la política tiene que percibir lo que cambia |

## El mapa de horas

| Hora | Bloque | Min |
|---|---|---|
| 15:00 | Preparar el PC + ignición | 20 |
| 15:20 | **1 · MODELAR**: el robot y su mundo | 65 |
| 16:25 | Descanso | 10 |
| 16:35 | **2 · EL ENTORNO Y EL RL**: el cerebro, la recompensa, PPO | 40 |
| 17:15 | **3 · ENTRENAR**: la voltereta, de cero a experto | 55 |
| 18:10 | Descanso | 10 |
| 18:20 | **3 · ENTRENAR**: configura tu entrenamiento real | 35 |
| 18:55 | **4 · DESPLEGAR**: ROS 2 y la partida de la rayuela | 35 |
| 19:30 | **4 · DESPLEGAR**: sim-to-real y cierre | 30 |

## Cómo encaja con la descripción oficial del taller y con el vídeo de referencia
| Bloque | Descripción oficial | El vídeo de referencia (de la simulación al despliegue) |
|---|---|---|
| **1 · Modelar** | MuJoCo y escenas propias | Modelo 3D → MJCF (piezas, articulaciones, actuadores) |
| **2 · El entorno y el RL** | Fundamentos de RL y PPO | El entorno: observaciones, acciones, terminación y recompensa |
| **3 · Entrenar** | Recompensa estilo mjlab y entrenamiento corto | El script de entrenamiento con PPO; ajustar la recompensa |
| **4 · Desplegar** | ROS 2 + ONNX: jugar la rayuela con visión, control y teleoperación | Del simulador al mundo real: calibrar, ruido, aleatorización, probar con empujones |

## Las cuatro etapas, con las preguntas de cada una (y con el Microduck)
| Etapa | La pregunta | En este taller |
|---|---|---|
| **1 · Modelar** | ¿Cómo es el robot, y qué le pasa físicamente? | Piezas, articulaciones, masa, fricción. El pato sin cerebro se cae en menos de 1 s |
| **2 · El entorno** | ¿Qué **ve** el cerebro, qué **puede hacer**, qué se **premia** y cuándo **acaba** el intento? | Un entorno = `reset()` + `step(acción)` + una recompensa. La patada a una casilla, la voltereta |
| **3 · Entrenar** | ¿Cómo mejora? ¿Cuántas rondas, cuántos robots, qué tan grandes son los ajustes? | PPO: el que tú entrenas en CPU, y el real en GPU |
| **4 · Desplegar** | ¿Aguanta fuera de la simulación? | Ruido, retrasos, otro suelo, otra masa. La brecha sim-to-real |

---

## 1 · MODELAR · 1.1 El robot en el simulador (30 min)
**Pregunta guía:** ¿Cómo es el robot por dentro, y qué le pasa físicamente?
*Teoría: del plano al gemelo digital: modelo 3D → STL → URDF → MJCF → MuJoCo. Un robot es un árbol de piezas con articulaciones.*

| Nivel | Archivo | Qué cambias | Qué ves |
|---|---|---|---|
| Esencial | `workshop-ia-fisica/exercises/n1_04_robot_por_dentro.py` | `ESCENA`, `POSE`, `MOSTRAR` (articulaciones, motores, centro de masa, colisiones…) | El robot montado con sus 14 motores y articulaciones dibujados, y el árbol del XML en la terminal |
| Esencial | `workshop-ia-fisica/exercises/n1_03_despiece.py` | `COLUMNAS`, `PIEZAS`, `NORMALIZAR` | Las 43 piezas 3D (STL) que forman al pato, sueltas y en cuadrícula |
| Esencial | `exercises_rayuela/n0_00_pato_sin_cerebro.py` | `FRICCION`, `FACTOR_MASA`, `EMPUJON`, `VELOCIDAD` | El pato sin IA se cae en menos de 1 s, hagas lo que hagas |
| Extra | `workshop-ia-fisica/exercises/n1_01_ver_pieza.py` | `PIEZA` | Cada pieza 3D del robot |

**Para leer en VS Code (sin ejecutar):** [`workshop-ia-fisica/robot/GUIA_DE_LECTURA.md`](workshop-ia-fisica/robot/GUIA_DE_LECTURA.md) te guía por `robot_groundcontact.xml` (el robot en XML) y `scene.xml` (la escena), con los números de línea.

**Te llevas:** un robot es un árbol de piezas con masa; y equilibrar no se arregla con una postura fija: hace falta un cerebro que reaccione.

## 1 · MODELAR · 1.2 El mundo: laboratorio de mundos (35 min)
**Pregunta guía:** ¿Qué rodea al robot, y cómo cambia lo que hace?
*Teoría: la escena es lo que rodea al robot: suelo, cielo, luz, gravedad, objetos.*

| Nivel | Archivo | Qué cambias | Qué ves |
|---|---|---|---|
| Esencial | `exercises_rayuela/n1_02_tu_escena.py` | `MUNDO` (luna, marte, hielo, desierto, noche), gravedad, rozamiento, colores, `OBJETOS` (caja, rampa, esfera, cilindro) | El mismo pato en mundos distintos; la pelota vuela en la Luna; un laberinto de cajas |
| Extra | `exercises_rayuela/n4_05_obstaculos.py` | `NIVEL` de 0 a 4, `CEREBRO` | Un circuito en crescendo: rampa, escalones, cuadrícula irregular, escombros |

**Te llevas:** el mundo es parte del problema; el mismo cerebro se comporta distinto en otro suelo o con otra gravedad (misma patada: 1,74 m en la Tierra, 3,85 m en la Luna).

## 2 · EL ENTORNO Y EL RL (40 min)
**Pregunta guía:** ¿Qué ve el cerebro, qué hace, qué se premia y cómo aprende?
*Teoría: aprender es como montar en bici; el bucle agente-entorno; la red neuronal es una función con botones; la recompensa; PPO.*

| Nivel | Archivo | Qué cambias | Qué ves |
|---|---|---|---|
| Esencial | `workshop-ia-fisica/exercises/n3_00_demo_con_cerebro.py` | Las teclas (andar, `Y` sentarse, `R` voltereta) | El mismo robot, ahora con IA: anda y se recupera de empujones |
| Esencial | `workshop-ia-fisica/exercises/n2_03_dentro_del_cerebro.py` | `CEREBRO` | Qué es una **política**: 61 números entran, 14 salen, en vivo |
| Esencial | `workshop-ia-fisica/exercises/n2_01_recompensa_en_vivo.py` | Los pesos de la recompensa | La nota del pato mientras lo empujas |
| Extra | `workshop-ia-fisica/exercises/n2_00_cerebro_en_vivo.py` | `QUITAR_SENTIDO`, `RUIDO_SENTIDOS`, `RUIDO_ORDENES` | Le quitas un sentido al cerebro o le metes ruido: ¿qué es lo que más necesita? |

**Te llevas:** un cerebro es una función (61 números → 14); la recompensa es una nota, y de cómo la diseñes depende lo que aprende. Diseñarla es lo difícil.

## 3 · ENTRENAR · 3.1 La voltereta: de cero a experto (55 min)
**Pregunta guía:** ¿Cómo aprende de verdad, y cómo sé que ha aprendido?
*Teoría: el ciclo del entrenamiento; checkpoints; los botones del entrenamiento (rondas, robots a la vez, tasa de aprendizaje, exploración); PPO de verdad.*
La voltereta es **una habilidad sencilla de describir** y difícil de aprender. Hay nueve **checkpoints** (copias del cerebro guardadas durante un entrenamiento real de 20.750 rondas).

| Nivel | Archivo | Qué cambias | Qué ves |
|---|---|---|---|
| Esencial | `workshop-ia-fisica/exercises/n3_07_voltereta_checkpoints.py` | `CHECKPOINT` (0, 500, 750, 1250, 3000, 7000, 11000, 20000, 20750) | El mismo robot en distintos momentos de su aprendizaje: pulsa `R` para la voltereta |
| Esencial | `workshop-ia-fisica/exercises/n3_08_voltereta_medir.py` | `CHECKPOINTS`, `INTENTOS` | Una tabla con números y la curva real. Medido: aparece a las 750 rondas, se vuelve irregular, se estabiliza hacia las 11.000, y **el 20.000 es peor que el 11.000** |
| Esencial | `exercises_rayuela/n3_05_entrena_la_patada.py` | Recompensa, `LEARNING_RATE`, `EXPLORACION`, `ITERACIONES`, `CASILLAS`… | **Entrenas tú, de verdad, en tu CPU (~3 min):** PPO sobre la patada; la curva sube de ~1 a ~8 aciertos de 9 |
| Extra | `workshop-ia-fisica/exercises/n3_04_curvas_entrenamiento.py` | Qué parámetro se cambió | Curvas reales de entrenamiento |
| Extra | `exercises_rayuela/n3_06_comparar_politicas.py` | Qué políticas comparas | Tu política frente a otras y frente a la oficial |

**Te llevas:** entrenar es una curva con altibajos: se guardan checkpoints, se **mide** y se **elige**. Y has entrenado tú un PPO de verdad.

## 3 · ENTRENAR · 3.2 Configura tu entrenamiento real (35 min)
**Pregunta guía:** ¿Qué hay que decidir antes de pulsar «entrenar», y cómo me lo llevo a casa?
*Teoría: mjlab, la herramienta real; una tarea = escena + observaciones + acciones + recompensa + algoritmo; GPU local o en la nube.*
Sin GPU no se puede entrenar con mjlab, pero **todo lo anterior al botón sí se prepara**. Cada ejercicio lee la configuración oficial, te deja cambiarla y escribe **tu paquete** (`mi_entrenamiento/<caso>/`) listo para lanzar en un PC con GPU o en la nube.

| Nivel | Archivo | Caso |
|---|---|---|
| Esencial | `exercises_rayuela/n6_00_entrenar_voltereta.py` | **La voltereta** (el caso de partida, con los valores del entrenamiento real) |
| Extra | `exercises_rayuela/n6_05_partir_de_lo_ya_entrenado.py` | **No empieces de cero:** parte de un cerebro que ya sabe andar (obstáculos, el duelo de la cuerda) |
| Extra | `exercises_rayuela/n6_01_entrenar_rayuela.py` | La Rayuela: patear a una casilla |
| Extra | `exercises_rayuela/n6_02_entrenar_cuerda.py` | El duelo de la cuerda (autojuego) |
| Extra | `exercises_rayuela/n6_03_entrenar_patines.py` | Los patines: otro cuerpo |
| Extra | `exercises_rayuela/n6_04_entrenar_obstaculos.py` | Obstáculos (GTC): terreno irregular |

**No empieces de cero (currículo entre políticas; se explica en la diapositiva 36 aunque no haya ejercicio).** Lo habitual es *subir*: se parte de una política que ya sabe lo básico (andar) y se le enseña lo siguiente.
Según las fichas de sus autores: `alpha_walking` → `rough_walk_e` (terreno irregular, **800 rondas**, la mitad de caídas) frente a `rough_walk_g` (desde cero, 3.300 rondas).
El duelo de la cuerda (dos patos que aprenden jugando entre sí) sale de ese mismo árbol: 6.000 rondas partiendo de su cerebro de andar.
En nuestro circuito: nivel 4 (escombros), `alpha_walking` 3 de 6 · `rough_walk_e` **5 de 6** · `rough_walk_g` 3 de 6 (un solo azar: orientativo).

En los ejercicios `n6_*` haces siempre lo mismo: **elegir la tarea → leer la recompensa real → cambiar un peso → generar el paquete → leer el comando**.

**Te llevas:** tu paquete de entrenamiento listo para una GPU, y el mapa «si algo falla, qué etapa tocas» (al final de este documento).

## 4 · DESPLEGAR · 4.1 ROS 2 y la partida de la rayuela (35 min)
**Pregunta guía:** ¿Cómo se mete una política en un sistema que juega?
*Teoría: una política es un fichero .onnx; nodos, topics y lanzadores; cómo encajan visión, control y teleoperación.*

| Nivel | Archivo | Qué cambias | Qué ves |
|---|---|---|---|
| Esencial | `exercises_rayuela/n4_01_ros2_en_vivo.py` | `VISION`, `CONTROL` | Los nodos y topics de la Rayuela oficial funcionando |
| Esencial | `exercises_rayuela/n4_00_partida_rayuela.py` | `TABLA_PROPIA`, `OBJETIVO`, `PUNTOS` | La partida con **tu** política: patada, visión y marcador |

**Te llevas:** un `.onnx` es un fichero que cualquier programa puede ejecutar; ROS 2 conecta visión, control y teleoperación con nodos y topics. (En Windows es una imitación en un proceso; el código oficial es el mismo.)

## 4 · DESPLEGAR · 4.2 Sim-to-real y cierre (30 min)
**Pregunta guía:** ¿Aguanta fuera de la simulación?
*Teoría: la brecha entre simulación y realidad; aleatorización de dominio; la lista antes de llevar una política al robot.*

| Nivel | Archivo | Qué cambias | Qué ves |
|---|---|---|---|
| Esencial | `exercises_rayuela/n5_01_generalizar.py` | `MUNDOS_PRUEBA`, `POLITICAS` | Se ejecuta ya (trae 3 políticas de ejemplo). Medido: entrenada en un solo mundo, 8/9 y se hunde (4,2 de media); con mundos al azar **a ciegas**, peor (2,0); **percibiendo el mundo, 8/9 y aguanta (6,8)** |
| Extra | `workshop-ia-fisica/exercises/n3_00_demo_con_cerebro.py` | `VOLTAJE_BATERIA` (6.5), `RETRASO_MOTORES` | Fallos típicos del robot real, simulados: batería baja, motores que obedecen tarde |
| Extra | `exercises_rayuela/n5_00_preparar_sim2real.py` | Nivel de dificultad | El contrato del .onnx y la robustez en crescendo |

**Te llevas:** aleatorizar el mundo no basta; la política tiene que poder percibir lo que cambia. Y nunca se despliega sin repasar la lista (contrato, robustez, vuelta atrás).

## Casos de uso (para casa, o si sobra tiempo)
| Archivo | Qué es |
|---|---|
| `exercises_rayuela/n4_02_patines.py` | El Microduck con ruedas |
| `exercises_rayuela/n4_03_cuerda.py` | El duelo de la cuerda: dos patos, una cuerda (`ETAPA_A` / `ETAPA_B` eligen una de las 9 etapas del entrenamiento) |
| `exercises_rayuela/n4_07_duelo_etapas.py` | ¿Más entrenado es mejor? Mide las etapas del duelo con una tabla |
| `exercises_rayuela/n4_04_equilibrio.py` | Empújalo y se corrige; pruébalo sobre un balancín |
| `exercises_rayuela/n4_06_validar_politicas.py` | Mide con números los cerebros en el circuito |

---

## Si algo falla, ¿qué etapa tocas?
Es la idea más útil de todo el taller. Con números que hemos medido nosotros (simulación, pocas semillas: orientativo).

| Lo que ves | Etapa | Qué tocas | Lo que hemos medido |
|---|---|---|---|
| **Se cae nada más empezar** | 1 · Modelar | Postura, masa, fricción… o le falta cerebro | El pato sin cerebro se cae en menos de 1 s y **ni la fricción ni la masa lo salvan** (`n0_00`) |
| **Cambia todo en otro mundo** | 1 · Modelar | Gravedad, suelo, objetos | Misma patada: 1,74 m en la Tierra y 3,85 m en la Luna (`n1_02`) |
| **La curva no sube: no aprende** | 3 · Entrenar | Tasa de aprendizaje, robots a la vez, exploración | Levantarse, 100 rondas: base 25,4 · tasa 0,00005 → 8,8 · tasa 0,01 → se descontrola · 256 robots → 6,1 · exploración 0,1 → −108 |
| **Aprende, pero con un truco raro** | 2 · Entorno (recompensa) | Los pesos, sobre todo los castigos | El primer entrenamiento de la voltereta, sin castigo por girar rápido, aprendió un **latigazo** violento (lo cuenta el propio fichero de la tarea) |
| **Solo acierta lo que vio** | 2 · Entorno (qué ve) | Que vea más variedad | Entrenar la patada solo con las casillas 3 y 7: acierta 2 de 9 frente a 8 (`n3_05`) |
| **Va bien, luego empeora, es irregular** | 3 · Entrenar | Guardar checkpoints, **medir** y elegir | Voltereta: 750 → 10/10; 3.000 → 4/10; 11.000 → 10/10; 20.000 → 3/10. **El último no siempre es el mejor** (`n3_07`, `n3_08`) |
| **Funciona en simulación, falla en otro mundo** | 4 · Desplegar | Entrenar con variedad, y que perciba lo que cambia | Un solo mundo: 8/9 y se hunde (4,2 de media) · variedad a ciegas: peor (2,0) · variedad percibiéndola: **6,8** (`n5_01`) |
| **Aprender desde cero cuesta demasiado** | 3 · Entrenar | Partir de un cerebro que ya sabe algo | Terreno irregular: 800 rondas partiendo de andar frente a 3.300 desde cero (`n6_05`) |

---

**Sin editar archivos:** `MJLAB.bat` abre `mini_mjlab`, con los mismos verbos que mjlab pero en CPU (`MJLAB list-envs`, `MJLAB params <entorno>`, `MJLAB play ...`, `MJLAB train ...`).

**Si algo falla:** envía `instalar_log.txt` al ponente; mira la tabla de problemas del [`README.md`](README.md).

**Si no tienes el PC a mano:** todo el taller se sigue con las diapositivas; los números medidos están en las notas de cada una.
