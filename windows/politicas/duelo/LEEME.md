# Nueve etapas del entrenamiento del duelo de la cuerda

Nueve **checkpoints** (copias del cerebro guardadas durante el entrenamiento) del duelo de la cuerda del proyecto `patos_cuerda` (Bravo Robots, rama `tug-etapas` de `microduck_rl`).
Es **una sola carrera continua de autojuego, de la iteración 0 a la 6.027** (en cuatro tandas: 0-3.222, 3.231-4.113, 4.122-5.811 y 5.820-6.027), con 676 checkpoints guardados; aquí van nueve.
La iteración 0 es el cerebro de **andar** del que se parte (checkpoint 10250 de locomoción); la **6.027 es la política publicada** (`../duelo2.onnx`: salida idéntica, diferencia máxima 0,0).

| Fichero | Iteración |
|---|---|
| `duelo_00000.onnx` | 0 (el cerebro de andar del que se parte) |
| `duelo_00500.onnx` | 500 |
| `duelo_01000.onnx` | 1.000 |
| `duelo_01500.onnx` | 1.500 |
| `duelo_02000.onnx` | 2.000 |
| `duelo_03000.onnx` | 3.000 |
| `duelo_04000.onnx` | 4.000 |
| `duelo_05000.onnx` | 5.000 |
| `duelo_06027.onnx` | 6.027 (la publicada) |

## Cómo se comporta cada etapa (medido en el simulador del taller)
Cada etapa juega de **pato A** contra un **cerebro que solo anda** (pato B, sin entrenar para el duelo), 12 combates por celda, semilla 4. «Gana / pierde / empata» es desde el punto de vista de A. «Caídas» cuenta las caídas de cualquiera de los dos.

| Etapa | Gana / pierde / empata | Caídas | Qué se ve |
|---|---|---|---|
| 0 | 2 / 0 / 10 | 0 | Es el que solo anda: tiran los dos y casi siempre empatan |
| 500 | 1 / 11 / 0 | 12 | El cambio de objetivo lo desordena: se cae casi siempre |
| 1.000 | **12** / 0 / 0 | 2 | Ya sabe tirar y gana todos |
| 1.500 | **12** / 0 / 0 | 7 | Igual |
| 2.000 | **12** / 0 / 0 | 7 | Igual |
| 3.000 | 6 / 1 / 5 | 6 | Irregular |
| 4.000 | 9 / 0 / 3 | 3 | Bien |
| 5.000 | **12** / 0 / 0 | 6 | Bien |
| 6.027 | 4 / **7** / 1 | 10 | **La publicada pierde más de lo que gana y se cae mucho** |

Con otras dos semillas (11 y 23) salió lo mismo: las etapas 1.000, 2.000 y 5.000 ganan 11-12 de 12; la 6.027 gana 5 y 4 de 12 (y pierde 6 y 8).
**Contra la etapa final (6.027 de pato B)**, las etapas 0 a 3.000 ganan los 12 combates, porque la final se cae siempre.

## Cómo leerlo (con cuidado)
- **Más entrenado no es mejor.** Es la misma lección que la voltereta: se guardan checkpoints, se mide y se elige. Aquí el mejor contra un rival que solo anda está hacia las 1.000-2.000 y las 5.000, no al final.
- Es **una medida en nuestro simulador de Windows** (MuJoCo + motores BAM + el cerebro ONNX), con 12 combates por celda y tres semillas: orientativa. No sabemos por qué la final se cae tanto; puede deberse a que se entrenó **solo contra copias de sí misma** (autojuego) y no ha visto rivales distintos.
- Mide tú mismo con `exercises_rayuela/n4_07_duelo_etapas.py` y míralas luchar con `n4_03_cuerda.py` (parámetros `ETAPA_A` y `ETAPA_B`).

## Cómo se hicieron los .onnx
Los `.pt` del entrenamiento se convirtieron a `.onnx` con el normalizador dentro (`(obs - media) / (desviación + 0,01)` y una red 61 -> 512 -> 256 -> 128 -> 14 con ELU), igual que el export oficial. Validado con `duelo2.onnx`: diferencia máxima 0,0.
Script: `herramientas_ponente/exportar_checkpoints_duelo.py` (necesita PyTorch; no se incluye en el repositorio de alumnos). Contrato de cada fichero: entrada `obs` (1 x 61), salida `actions` (1 x 14), 50 Hz. Origen: `microduck_rl` (Pollen Robotics / Bravo Robots), Apache-2.0.
