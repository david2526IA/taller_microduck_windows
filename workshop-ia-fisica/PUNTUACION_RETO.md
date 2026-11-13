# Hoja de puntuación — "haz que falle / haz que gane"

Parejas. Cada pareja prueba **3 rondas de 60 s** con `exercises/n3_02_marcador.py`, que cuenta solo los segundos de pie y los empujones y da los puntos (también vale la demo normal, contando a mano).

**Puntos de la ronda = segundos de pie (máx. 60) − empujones usados**

| Pareja | Equipo (A: tira / B: aguanta) | Opciones usadas (suelo, `--vin`, `--delay`, `--action-scale`, cerebro) | Seg. de pie | Empujones | Puntos |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |

**Reglas**
- Un empujón = un Ctrl + clic derecho arrastrando sobre el robot.
- El equipo A elige las condiciones para que el robot **falle**; el equipo B, para que **gane**. Luego se cambian los papeles.
- Gana la pareja con más puntos sumando las 3 rondas.
- Vale cambiar: el suelo (`scene.xml`), la batería, el retraso, la potencia y el cerebro (`progresion_*.onnx`).
