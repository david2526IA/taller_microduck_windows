# Politicas propias (.onnx)

| Fichero | Que es | De donde viene |
|---|---|---|
| `duelo2.onnx` | Cerebro del **duelo de la cuerda** (autojuego, 61 entradas y 14 salidas) | Proyecto `patos_cuerda` (Bravo Robots): carrera `2026-10-08_22-18-18_duelo2` de la rama `tug-etapas` de `microduck_rl`, hasta la iteracion 6027, exportada a ONNX por el propio entrenamiento. Entrenado con mjlab + PPO en GPU. |

Recompensas del entrenamiento (perfil DUELO): `competitive_terminal=200, timeout_stalemate=-8, fall_duel=0, fall_any=-20, pull_back_taut=10, rope_taut=0.5, tug_pull_velocity=4`.
Reglas: gana quien consigue que el otro cruce su linea (x = -0,35 azul, x = +0,35 roja) o se caiga; empate a los 20 s.
Se parte del cerebro de locomocion `model_10250` (andar con orden de velocidad), por eso necesita una orden de avance como entrada.

## Politicas para terreno irregular (descargadas de Hugging Face)

| Fichero | Que es | Origen y licencia |
|---|---|---|
| `rough_walk_e.onnx` | Andar con orden de velocidad, **afinado 800 iteraciones** sobre terreno hostil a partir de `alpha_walking`. Segun su ficha: la mitad de caidas que `alpha_walking` en su bateria de pruebas (14 de 110 frente a 32 de 110) | [RemiFabre/microduck-rough-walk-e](https://huggingface.co/RemiFabre/microduck-rough-walk-e), **Apache-2.0**. Entrenado con `pollen-robotics/microduck_rl` (rama `hostile-terrain`, commit `6cd45fc`) |
| `rough_walk_g.onnx` | Lo mismo, **entrenado desde cero** 3300 iteraciones en terreno irregular: el mas firme en escalones pequenos y rampas, con un 17 % mas de potencia de motor | [RemiFabre/microduck-rough-walk-g](https://huggingface.co/RemiFabre/microduck-rough-walk-g), **Apache-2.0** |

Los dos tienen el mismo contrato que `alpha_walking` (61 entradas, 14 salidas, 50 Hz): se cambian uno por otro sin tocar nada mas.
Limites que declaran sus autores: solo probados en simulacion; fallan al bajar escalones de 2 cm o mas.
Las fichas completas (`manifest.json`) estan al lado. Descargadas el 12 nov 2026.
