# PROBAR EL TALLER, paso a paso (Windows)

Orden del itinerario oficial (15:00-20:00). Cada ejercicio se lanza con **F5** en VS Code, o desde la terminal:

```powershell
workshop-ia-fisica\.venv\Scripts\python.exe exercises_rayuela\NOMBRE.py
```

(o con doble clic en `lanzar.bat NOMBRE` desde la carpeta del proyecto). **Las teclas se pulsan en la terminal**, no en la ventana del robot.
**El ciclo de siempre:** cambia UN valor de la lista de parametros de arriba del fichero → guarda (Ctrl+S) → **cierra la ventana del robot** → lanza otra vez.

> Antes de nada: `INSTALAR_TODO.bat` (clona los repos y prepara Python 3.12 + MuJoCo + OpenCV). Si usas una carpeta de OneDrive, pausa la sincronizacion: pesa >1 GB.

## 1 · Simulacion MuJoCo (qué es y cómo se describe un mundo)

| Ejercicio | Qué hace | Parámetros (y en qué afectan) | Qué observar |
|---|---|---|---|
| `workshop-ia-fisica\exercises\n1_00_ver_robot.py` | El robot en el visor | `POSE` (STAND/SIT/FOLD) | Ctrl + clic derecho lo empuja |
| `workshop-ia-fisica\exercises\n1_01_ver_pieza.py` | Una pieza 3D suelta | `PIEZA` | Que el robot son mallas + masas + motores |
| **`n1_02_tu_escena.py`** | La rayuela en un mundo que TÚ editas | `GRAVEDAD` (Luna=1.62), `ROZAMIENTO_SUELO` (hielo=0.1), `ESCALA_MASA_PATO`, `RADIO_PELOTA`, `MASA_PELOTA`, `OBSTACULOS` (cajas), `COLOR_TABLERO` | El cerebro se entrenó en la Tierra: en la Luna o con hielo se nota. ¿Sigue detectando la pelota la visión con un tablero oscuro? |

## 2 · Fundamentos de RL (agente, entorno, observaciones, acciones, recompensas, PPO)

| Ejercicio | Qué hace | Parámetros | Qué observar |
|---|---|---|---|
| `workshop-ia-fisica\exercises\n2_00_cerebro_en_vivo.py` | Las 61 entradas y 14 salidas del cerebro, en vivo | `QUITAR_SENTIDO`, `RUIDO_SENTIDOS`, `RUIDO_ORDENES` | A qué sentidos hace caso |
| `workshop-ia-fisica\exercises\n2_01_recompensa_en_vivo.py` | La recompensa como suma de piezas × pesos | `PESO_ALTURA`, `PESO_VERTICAL`, `PESO_AVANZAR`, `PESO_ESFUERZO` | Qué truco aprendería si solo premias avanzar |
| `workshop-ia-fisica\exercises\n2_03_dentro_del_cerebro.py` | Las capas de la red | `CEREBRO`, `APAGAR_CAPA1` | Aguanta con el 99 % de neuronas apagadas |
| **`n3_05_entrena_la_patada.py`** | **PPO de verdad, en tu CPU**, ~2 min | Recompensa: `PESO_PRECISION`, `BONUS_ACIERTO`, `PENALIZA_CAIDA`, `PESO_FUERZA`. PPO: `ITERACIONES`, `PATADAS_POR_RONDA`, `LEARNING_RATE`, `CLIP`, `EPOCAS`, `EXPLORACION`, `COEF_ENTROPIA`, `SEMILLA`. Entorno: `CASILLAS`, `GRAVEDAD`, `MASA_PELOTA`, `ROZAMIENTO_PELOTA` | Curva de recompensa subiendo y tabla ANTES/DESPUÉS (con los valores por defecto pasa de ~1 a ~6 aciertos de 9). Prueba `LEARNING_RATE = 0.5` (se descontrola), `EXPLORACION = 0.02` (se atasca), `PESO_FUERZA = 0.5` (se queda corto) |

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

## Lo que está probado y lo que no

- **Probado sin ventana (arranca y se comporta):** `n4_00` (patada → visión → control → llega a la casilla), `n4_01`, `n1_02`, `n3_05` (entrena y mejora), `n4_03` (cuerda tensa, patos de pie), `n4_04` (empujones medidos, con y sin plataforma), `n4_02` (arranca).
- **Sin probar con ventana abierta ni con teclado real:** ninguno. Lo primero que conviene mirar: que el visor se abra, que las teclas respondan y que la fluidez sea aceptable (la Rayuela con cámara va por debajo del tiempo real en este PC: unos 19 pasos/s de simulación frente a 50).
- **`n4_02_patines`:** la tecla `n` (nueva partida) está escrita pero no probada.
- **Límites conocidos:** entrenar con mjlab y GPU no se ejecuta aquí; ROS 2 es una versión en miniatura en un solo proceso (`windows\ros_shim\`), no ROS 2 real.
