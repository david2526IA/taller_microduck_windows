# Checkpoints de la voltereta

Nueve **checkpoints** (copias del cerebro guardadas durante el entrenamiento) de la voltereta hacia delante del Microduck
(tarea `Mjlab-Roulade-Flat-MicroDuck`). Vienen de un entrenamiento REAL en GPU, de 20.750 rondas, hecho en varias tandas
(carrera 2026-09-09_13-51-09 hasta la ronda 8.750; despues se reanudo hasta la 13.000, 14.000 y 20.750).

| Fichero | Ronda | Salen bien (de 10) | Que se observa |
|---|---|---|---|
| `voltereta_00000.onnx` | 0 | 0 | recien nacido: se queda quieto |
| `voltereta_00500.onnx` | 500 | 0 | todavia nada |
| `voltereta_00750.onnx` | 750 | 10 | aparece la voltereta |
| `voltereta_01250.onnx` | 1.250 | 9 | casi siempre |
| `voltereta_03000.onnx` | 3.000 | 4 | irregular: a veces gira, a veces no |
| `voltereta_07000.onnx` | 7.000 | 5 | sigue irregular |
| `voltereta_11000.onnx` | 11.000 | 10 | estable |
| `voltereta_20000.onnx` | 20.000 | 3 | el penultimo guardado: peor que el 11.000 |
| `voltereta_20750.onnx` | 20.750 | 10 | el final |

**Como se midio** (`windows/voltereta_env.py`, ejercicio `n3_08_voltereta_medir.py`): en el simulador del taller (MuJoCo + motores BAM), 10 intentos por checkpoint,
cada uno con el robot de pie tras esperar de 0,8 a 1,7 s. "Sale bien" = el tronco gira mas de 300 grados hacia delante Y el robot acaba de pie. Es una medida
en simulacion; no se ha probado en el robot real.

`curva_entrenamiento.csv`: recompensa media y duracion de episodio por ronda (cada 50) del entrenamiento real (de -0,9 a 35,3). Se han quitado 3 puntos: el primero de cada tanda reanudada (rondas 8.750, 13.000 y 14.000), que no es representativo.

## Como se hicieron los .onnx
Los `.pt` del entrenamiento se convirtieron a `.onnx` con el normalizador dentro (`(obs - media) / (desviacion + 0,01)` y una red 61 -> 512 -> 256 -> 128 -> 14 con ELU),
igual que el export oficial de mjlab. Se comprobo con el `.onnx` oficial de la misma carrera: diferencia maxima 0,0.
El script esta en el repositorio del ponente (`herramientas_ponente/exportar_checkpoints_voltereta.py`); necesita PyTorch.

Contrato de cada .onnx: entrada `obs` (1 x 61), salida `actions` (1 x 14), 50 Hz. Origen: proyecto `microduck_rl` (Pollen Robotics / Bravo Robots), Apache-2.0.
