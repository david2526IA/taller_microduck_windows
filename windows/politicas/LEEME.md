# Politicas propias (.onnx)

| Fichero | Que es | De donde viene |
|---|---|---|
| `duelo2.onnx` | Cerebro del **duelo de la cuerda** (autojuego, 61 entradas y 14 salidas) | Proyecto `patos_cuerda` (Bravo Robots): carrera `2026-10-08_22-18-18_duelo2` de la rama `tug-etapas` de `microduck_rl`, hasta la iteracion 6027, exportada a ONNX por el propio entrenamiento. Entrenado con mjlab + PPO en GPU. |

Recompensas del entrenamiento (perfil DUELO): `competitive_terminal=200, timeout_stalemate=-8, fall_duel=0, fall_any=-20, pull_back_taut=10, rope_taut=0.5, tug_pull_velocity=4`.
Reglas: gana quien consigue que el otro cruce su linea (x = -0,35 azul, x = +0,35 roja) o se caiga; empate a los 20 s.
Se parte del cerebro de locomocion `model_10250` (andar con orden de velocidad), por eso necesita una orden de avance como entrada.
