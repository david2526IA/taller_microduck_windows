# PROBAR EL TALLER, paso a paso (Windows)

Orden del itinerario oficial (15:00-20:00). Cada ejercicio se lanza con **F5** en VS Code, o desde la terminal:

```powershell
workshop-ia-fisica\.venv\Scripts\python.exe exercises_rayuela\NOMBRE.py
```

(o con doble clic en `lanzar.bat NOMBRE` desde la carpeta del proyecto). **Las teclas se pulsan en la terminal**, no en la ventana del robot.
**El ciclo de siempre:** cambia UN valor de la lista de parametros de arriba del fichero → guarda (Ctrl+S) → **cierra la ventana del robot** → lanza otra vez.

> **Atajo sin editar ficheros:** `MJLAB.bat` (o `workshop-ia-fisica\.venv\Scripts\python.exe mini_mjlab.py ...`) tiene los mismos verbos que mjlab, en CPU:
> `list-envs` (los entornos) · `params <entorno>` (qué se puede cambiar) · `play <entorno> --set NOMBRE=VALOR` · `train Mini-Kick-MicroDuck` · `validate Mini-Obstacles-MicroDuck`.
> Ejemplo: `MJLAB play Mini-Obstacles-MicroDuck --set NIVEL=3 --set CEREBRO=rough_walk_e`.

> Antes de nada: `INSTALAR_TODO.bat` (clona los repos y prepara Python 3.12 + MuJoCo + OpenCV). Si usas una carpeta de OneDrive, pausa la sincronizacion: pesa >1 GB.

## 1 · Simulacion MuJoCo (qué es y cómo se describe un mundo)

| Ejercicio | Qué hace | Parámetros (y en qué afectan) | Qué observar |
|---|---|---|---|
| `workshop-ia-fisica\exercises\n1_03_despiece.py` | **El despiece:** las 43 piezas 3D (STL) del pato, sueltas y en cuadrícula | `COLUMNAS`, `PIEZAS`, `NORMALIZAR` | De qué piezas está hecho el robot; compara el pie izquierdo y el derecho |
| `workshop-ia-fisica\exercises\n1_04_robot_por_dentro.py` | **El robot y la escena por dentro:** las articulaciones, los motores, el centro de masa y las piezas de colisión dibujados sobre el robot; imprime el árbol del XML | `ESCENA`, `POSE`, `MOSTRAR`, `FISICA` | 15 piezas, 14 motores; las piezas de colisión son mucho más simples que las bonitas |
| `workshop-ia-fisica\exercises\n1_01_ver_pieza.py` | Una pieza 3D suelta | `PIEZA` | Que el robot son mallas + masas + motores |
| **`n1_02_tu_escena.py`** | **Laboratorio de mundos:** la rayuela en un mundo que TÚ editas | `MUNDO` (tierra, luna, marte, hielo, desierto, noche), `GRAVEDAD`, `ROZAMIENTO_SUELO`, `COLOR_SUELO_1/2`, `COLOR_CIELO_ARRIBA/ABAJO`, `ESCALA_MASA_PATO`, `RADIO_PELOTA`, `MASA_PELOTA`, `OBJETOS` (caja, rampa, esfera, cilindro), `COLOR_TABLERO` | El cerebro se entrenó en la Tierra: en la Luna o sobre hielo se nota. ¿Sigue detectando la pelota la visión con un suelo oscuro? Reto: un laberinto de cajas hasta la casilla 9. |
| **`workshop-ia-fisica/exercises/n3_07_voltereta_checkpoints.py`** | **La voltereta, checkpoint a checkpoint:** el mismo robot en 9 momentos de un entrenamiento real de 20.750 rondas | `CHECKPOINT` (0, 500, 750, 1250, 3000, 7000, 11000, 20000, 20750), perturbaciones opcionales | Pulsa `R`. El 0 no hace nada; el 750 ya gira; el 3.000 y el 7.000 son irregulares; el 11.000 y el 20.750 son estables. |
| **`workshop-ia-fisica/exercises/n3_08_voltereta_medir.py`** | **La voltereta, con números:** cada checkpoint intenta la voltereta varias veces sin ventana, más la curva real | `CHECKPOINTS`, `INTENTOS` | Medido (10 intentos): 0→0, 500→0, 750→10, 1250→9, 3000→4, 7000→5, 11000→10, 20000→3, 20750→10. El último no siempre es el mejor. |
| **`n6_00_entrenar_voltereta.py`** | **Configura tu entrenamiento real** (la voltereta) y escribe tu paquete en `mi_entrenamiento/voltereta/` | `NUM_ENVS`, `ITERACIONES`, `GUARDAR_CADA`, `LEARNING_RATE`, `ENTROPIA`, `GAMMA`, `PESOS` | Lee la recompensa oficial (19 términos con su significado) y genera los scripts para una GPU o la nube. No se puede entrenar aquí: no hay GPU. |
| **`n6_05_partir_de_lo_ya_entrenado.py`** | **Currículo entre políticas:** no empieces de cero, parte de un cerebro que ya sabe andar (o del duelo de la cuerda) | `CASO`, `PARTIR_DE_UNO_YA_ENTRENADO`, `CHECKPOINT_BASE`, `ITERACIONES` | Muestra el árbol de políticas con datos reales (800 rondas partiendo de la base frente a 3.300 desde cero) y escribe el paquete con `--agent.load-checkpoint`. |
| **`n6_01..04_entrenar_*.py`** | Lo mismo para la **Rayuela**, la **cuerda**, los **patines** y los **obstáculos** (GTC) | Como el anterior + `CONSTANTES` de la tarea | Cada uno lee la recompensa real de su tarea. La cuerda depende de los parches del proyecto patos_cuerda. |
| **`n5_01_generalizar.py`** | **Generalizar:** tres políticas de ejemplo probadas en 6 mundos distintos | `POLITICAS`, `MUNDOS_PRUEBA` | Una entrenada en un solo mundo acierta 8/9 y se hunde al cambiar el mundo (4,2 de media); aleatorizar a ciegas empeora (2,0); la que percibe el mundo aguanta (6,8). Entrena las tuyas con `ALEATORIZAR` y `VE_EL_MUNDO` en `n3_05` |

## 2 · Fundamentos de RL (agente, entorno, observaciones, acciones, recompensas, PPO)

| Ejercicio | Qué hace | Parámetros | Qué observar |
|---|---|---|---|
| `workshop-ia-fisica\exercises\n2_00_cerebro_en_vivo.py` | Las 61 entradas y 14 salidas del cerebro, en vivo | `QUITAR_SENTIDO`, `RUIDO_SENTIDOS`, `RUIDO_ORDENES` | A qué sentidos hace caso |
| `workshop-ia-fisica\exercises\n2_01_recompensa_en_vivo.py` | La recompensa como suma de piezas × pesos | `PESO_ALTURA`, `PESO_VERTICAL`, `PESO_AVANZAR`, `PESO_ESFUERZO` | Qué truco aprendería si solo premias avanzar |
| `workshop-ia-fisica\exercises\n2_03_dentro_del_cerebro.py` | Las capas de la red | `CEREBRO`, `APAGAR_CAPA1` | Aguanta con el 99 % de neuronas apagadas |
| **`n3_05_entrena_la_patada.py`** | **PPO de verdad, en tu CPU**, ~3 min | Recompensa: `PESO_PRECISION`, `BONUS_ACIERTO`, `PENALIZA_CAIDA`, `PESO_FUERZA`. PPO: `ITERACIONES`, `PATADAS_POR_RONDA`, `LEARNING_RATE`, `CLIP`, `EPOCAS`, `EXPLORACION`, `COEF_ENTROPIA`, `SEMILLA`. Entorno: `CASILLAS`, `GRAVEDAD`, `MASA_PELOTA`, `ROZAMIENTO_PELOTA` | Curva de recompensa subiendo y tabla ANTES/DESPUÉS (con los valores por defecto pasa de ~1 a ~6 aciertos de 9). Prueba `LEARNING_RATE = 0.5` (se descontrola), `EXPLORACION = 0.02` (se atasca), `PESO_FUERZA = 0.5` (se queda corto) |
| **`n3_06_comparar_politicas.py`** | **Varias políticas, comparadas:** entrena con distintas recompensas (cambia `NOMBRE_POLITICA` y `PESO_FUERZA` en `n3_05`) y compáralas con la tabla oficial | `POLITICAS`, `INCLUIR_OFICIAL`, `REPETICIONES` | Medido (semilla 0): 20, 30 y 60 rondas → 4, 7 y 8 de 9; `LEARNING_RATE = 0.5` → 0; solo casillas 3 y 7 → 2 (no generaliza). Sorpresas: `EXPLORACION = 0.02` y `PESO_FUERZA = 0.5` → 9 de 9 |

## 3 · Práctica con mjlab: diseñar la recompensa y ver cómo cambia la conducta

| Dónde | Qué | Para qué |
|---|---|---|
| `n3_05_entrena_la_patada.py` | La función `recompensa()` es la recompensa de la patada, legible y editable | Cambiar un peso y volver a entrenar = ver cómo cada cambio altera la conducta |
| `rayuela-oficial\src\mjlab_microduck\tasks\` | Las recompensas y tareas reales de mjlab (BallKickSpeed, etc.) | Leer cómo se define lo mismo en el entrenamiento de verdad (GPU) |
| `workshop-ia-fisica\entrenar\ENTRENAR.md` y `n3_04_curvas_entrenamiento.py` | Cómo se lanza un entrenamiento real y curvas reales de 6 experimentos | Qué hace cada opción y cómo se leen las curvas |

> El entrenamiento real de mjlab necesita GPU NVIDIA: no se ejecuta en estos PCs. `n3_05` enseña el mismo bucle a escala pequeña.

## 4 · ROS 2 y la partida completa (nodos, topics, lanzadores, políticas ONNX con visión, control y teleoperación)

| Ejercicio | Qué hace | Parámetros | Qué observar |
|---|---|---|---|
| **`n4_01_ros2_en_vivo.py`** | Tabla de los topics de ROS 2 con mensajes/segundo | `VISION`, `CONTROL`, `VER_VISION` | Con `VISION = False`, `/rayuela/target_casilla` se queda en 0 |
| **`n4_00_partida_rayuela.py`** | **La partida:** patea la pelota a la casilla pedida. Visión y control oficiales | `OBJETIVO` (1-9 / "aleatorio"), `VELOCIDAD_PATADA`, `TABLA_PROPIA` (tu política de `n3_05`), `PUNTOS`, `VISION`, `CONTROL`, `VER_VISION` | Teclas: `k`/`l` patada a TU velocidad, `1`-`9` patada automática, `h` a casa, `n` ronda nueva. Calibra: ¿qué velocidad da la casilla 5? |

Después de `n3_05`, pon en `n4_00` → `TABLA_PROPIA = AQUI_RAIZ / "mi_tabla_patada.json"` y compara **tu política** con la oficial.

## 5 · Casos de uso (se ve cómo se llega a todo esto)

| Ejercicio | Qué hace | Parámetros | Qué observar |
|---|---|---|---|
| **`n4_02_patines.py`** | El Microduck sobre patines (otro cuerpo, otro cerebro) | `VOLTAJE_BATERIA`, `RETRASO_MOTORES`, `POTENCIA_MOTORES`, `ROZAMIENTO`, `CEREBRO_RODAR`, `CEREBRO_QUIETO` | Teclas: flechas, `p` empujón, `n` nueva partida. Con retraso el equilibrio se rompe |
| **`n4_03_cuerda.py`** | **El duelo de la cuerda con una política ENTRENADA** (proyecto `patos_cuerda`): dos Microducks atados, gana quien cruza la línea contraria o hace caer al otro | `AVANCE_A/B` (cuánto tira cada uno), `FUERZA_B`, `MASA_A/B`, `ROZAMIENTO_SUELO`, `LARGO_CUERDA`, `DESPLAZAMIENTO`, `RUIDO_INICIAL`, `B_SOLO_ANDA` (B sin entrenar para el duelo), `TIEMPO_MAX` | Teclas `w/s` e `i/k` para que cada uno tire más o menos, `n` combate nuevo. Prueba `B_SOLO_ANDA = True`: ¿cuánto aporta entrenar con recompensa competitiva? |
| **`n4_04_equilibrio.py`** | **Laboratorio de equilibrio** (sin rayuela): el Microduck de pie con su cerebro de equilibrio; tú lo empujas o le mueves el cuerpo y él se autocorrige. Mide cuánto tarda en recuperarse | `EMPUJON`, `VOLTAJE_BATERIA`, `RETRASO_MOTORES`, `POTENCIA_MOTORES`, `ROZAMIENTO`, `CEREBRO_QUIETO/ANDAR`, y `PLATAFORMA` (una tabla-balancín: `INCLINACION_MAX`, `RIGIDEZ_MUELLE`, `AMORTIGUACION`, `MASA_TABLA`) | Teclas: `p` empujón, `b` modo postura (flechas = altura e inclinación del cuerpo), `n` nueva prueba. Medido: con `EMPUJON = 0.4` se recupera siempre; con 0.8 falla a veces. ¿Qué pasa con `RETRASO_MOTORES = 2`? |
| **`n5_00_preparar_sim2real.py`** | **Preparar el sim-to-real:** contrato del `.onnx` (61→14, 32 bits, ≤ 64 MiB), robustez en crescendo (rozamiento, masa, batería, retraso, empujones) y lista de despliegue al robot | `CEREBROS` (o la ruta a TU `.onnx`), `PRUEBAS`, `NIVEL_MAX`, `ROZAMIENTO`, `MASA`, `VOLTAJE_BAJO`, `RETRASO`, `EMPUJON` | ¿En qué nivel empiezan las caídas de cada cerebro? (Los entrenados en terreno irregular recuperan peor los empujones.) |
| **`n4_05_obstaculos.py`** | **El circuito de obstáculos** (inspirado en la demo de NVIDIA del GTC Berlín 2026): el pato anda solo por rampa, escalones, cuadrícula irregular y escombros, y avisa de la sección, de dónde se cae y de la meta | `NIVEL` (0 llano … 4 todo: es el **crescendo**), `CEREBRO` (`alpha_walking`, `rough_walk_e`, `rough_walk_g`), `AVANCE_AUTOMATICO`, `MANTENER_RUMBO`, `ANGULO_RAMPA`, `N_ESCALONES`, `ALTURA_ESCALON`, `ALTURA_CUADRICULA`, `ALTURA_ESCOMBROS`, `SEMILLA_CIRCUITO` | Sube `NIVEL` de 0 a 4: ¿en cuál se cae cada cerebro? Sube `ALTURA_ESCALON` a 0.02 |
| **`n4_06_validar_politicas.py`** | **Validar con números**, como la validación de NVIDIA: cada cerebro en cada nivel, con circuitos completados y caídas; guarda un CSV | `PRUEBAS`, `CEREBROS`, `NIVELES`, `AVANCE`, `MANTENER_RUMBO` y las alturas del circuito | Medido aquí (6 pruebas, ruido alto): los tres completan llano y rampa; en escalones, cuadrícula y escombros se separan |

## Lo que está probado y lo que no

- **Descargado de Hugging Face (Apache-2.0):** `rough_walk_e` y `rough_walk_g` (en `windows/politicas/`, con su procedencia).
- **Probado sin ventana (arranca y se comporta):** `n4_00` (patada → visión → control → llega a la casilla), `n4_01`, `n1_02`, `n3_05` (entrena y mejora), `n4_03` (cuerda tensa, patos de pie), `n4_04` (empujones medidos, con y sin plataforma), `n4_02` (arranca).
- **Sin probar con ventana abierta ni con teclado real:** ninguno. Lo primero que conviene mirar: que el visor se abra, que las teclas respondan y que la fluidez sea aceptable (la Rayuela con cámara va por debajo del tiempo real en este PC: unos 19 pasos/s de simulación frente a 50).
- **`n4_02_patines`:** la tecla `n` (nueva partida) está escrita pero no probada.
- **Límites conocidos:** entrenar con mjlab y GPU no se ejecuta aquí; ROS 2 es una versión en miniatura en un solo proceso (`windows\ros_shim\`), no ROS 2 real.
