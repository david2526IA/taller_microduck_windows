# Cuaderno de misiones · Laboratorio del Bloque 4

Trabaja a tu ritmo. Cada misión es corta: **haces una cosa, miras qué pasa y lo anotas**.
- **N1** = solo ejecutas y miras. **N2** = cambias 1 ó 2 valores en un archivo.
- Para ejecutar un archivo: ábrelo en VS Code y pulsa **F5**.
- Las teclas de la demo se pulsan **en la terminal**, no en la ventana del robot. **Q** cierra.
- Empujar al robot: **Ctrl + clic derecho** arrastrando sobre él.
- Los números que ves pueden variar un poco de un PC a otro. Lo importante es **qué cambia y por qué**.

---

## A · Ver actuar a la IA (10 min)

**Misión 1 · Anda (N1)** — Abre `exercises/n3_00_demo_con_cerebro.py` y F5. Pulsa **↑** cuatro veces, prueba **← →**, **A / E**, **Y** (sentarse) y **R** (voltereta).
👀 ¿Qué tecla te ha sorprendido más? ______________________

**Misión 2 · Lee las opciones (N2)** — En la terminal: `python scripts/infer_policy.py --help`. Busca estas cuatro y apunta qué crees que hace cada una:
`--vin` ______ · `--delay` ______ · `--action-scale` ______ · `--foot-friction` ______

---

## B · Perturbar el mundo (20 min)

**Misión 3 · Empújalo (N1)** — Con el robot andando, empújalo con Ctrl + clic derecho.
👀 ¿Cuántos empujones aguanta antes de caerse? ______ ¿Se recupera solo? ______

**Misión 4 · Hielo y goma (N1)** — Abre `robot/scene.xml`, busca `friction=" 1 ..."` y cámbialo a **0,1** (hielo). Guarda (Ctrl+S) y lanza la demo.
👀 ¿Qué pasa al andar? ______ Prueba **2** (goma). ¿Y ahora? ______ **Déjalo otra vez en 1** al terminar.

**Misión 5 · El límite del hielo (N2)** — Abre `exercises/n3_02_marcador.py`. Pon `ROZAMIENTO_PIES = 0.3` y F5, luego `0.1`.
👀 ¿Con cuál se cae? ______ ¿Qué valor entre los dos es el límite? ______

**Misión 6 · Motores que obedecen tarde (N2)** — En el mismo archivo, pon `RETRASO_MOTORES = (2, 4)` y luego `(4, 6)`.
👀 ¿Con cuál se cae? ______ Esto es lo que pasa en un robot real con la comunicación lenta.

**Misión 7 · Motores débiles (N2)** — `POTENCIA_MOTORES = 0.7` y luego `0.5`.
👀 ¿Hasta dónde aguanta? ______

**Misión 8 · Batería baja (N2)** — `VOLTAJE_BATERIA = 6.5` y luego `6.0`.
👀 ¿Se nota? ______ Pista: el cerebro se entrenó con voltajes entre 6,5 y 8,2 V. **¿Por qué crees que un valor dentro de ese rango casi no molesta?** ______________________

---

## C · Comparar cerebros (10 min)

**Misión 9 · Sin cerebro frente a con cerebro (N1)** — Ejecuta `exercises/n2_02_sin_cerebro.py` (se cae en menos de 1 s) y luego `n3_00_demo_con_cerebro.py`.
👀 ¿Qué hace el cerebro que no hace una postura fija? ______________________

**Misión 10 · De recién nacido a bien entrenado (N1)** — Abre `exercises/n3_01_progresion.py`, cambia `NIVEL` de 0 a 5 y F5 cada vez. Pulsa **↑** y empuja.

| Nivel | ¿Qué hace? |
|---|---|
| 0 recién nacido | |
| 1 quieto | |
| 2 tambaleante | |
| 3 bien | |
| 4 mejor | |
| 5 oficial | |

**Misión 11 · Cambia de cerebro (N2)** — En `n3_02_marcador.py` cambia `ANDAR = "policies/alpha_walking.onnx"` por `"policies/progresion_2_tambaleante.onnx"` y compara los **PUNTOS** con el oficial.
👀 ¿Cuál puntúa más? ______ ¿Por qué? ______

---

## D · Entrenar un cerebro (25 min)

Hoy **no se entrena nada** (no hace falta GPU). Las curvas de abajo son **reales**, sacadas entrenando
el mismo robot (levantarse del suelo, 100 rondas) cambiando **un solo parámetro** cada vez.

Abre `exercises/n3_04_curvas_entrenamiento.py` y F5. **Regla de oro: primero apunta tu predicción, luego marca la casilla.**

**Misión 12 · Más robots a la vez (N1)** — Lee «Pocos robots» (256 robots en vez de 4096).
🔮 Predicción: ¿aprenderá más rápido, igual o más lento? ______ ¿Por qué? ______
👀 Resultado: ¿cuánta recompensa tiene en la ronda 100? ______ ¿Y cuánto tardó en minutos? ______
Ahora cambia el **eje a Minutos**: ¿quién va mejor *en el mismo tiempo*? ______

**Misión 13 · Pasos grandes y pasos pequeños (N1)** — Mira «Aprendizaje alto» y «Aprendizaje bajo» (*learning rate*: cuánto se mueven los botones en cada ajuste).
🔮 Predicción de cada uno: ______________________
👀 ¿Cuál se descontrola (la gráfica avisa)? ______ ¿Cuál se queda corto? ______ ¿Qué valor te parece el mejor? ______

**Misión 14 · Probar cosas raras (N1)** — Mira «Mucha exploración» (*entropy*) y la gráfica **Exploración**.
🔮 Predicción: ¿ayuda probar muchas más cosas? ______
👀 ¿Qué le pasa a la recompensa? ______ ¿Y a la exploración, comparada con la base (que va bajando)? ______
💭 ¿Por qué un robot necesita probar cosas al principio, pero decidirse después? ______________________

**Misión 15 · El futuro importa (N1)** — Mira «Miope» (*gamma* 0,8: solo cuenta lo inmediato).
🔮 Predicción: ¿le irá peor que a la base? ______
👀 ¿Qué pasa de verdad? ______ Pista: en esta tarea el robot recibe puntos **en cada paso** mientras está de pie.
💭 ¿En qué tarea sí haría falta mirar lejos? (Pista: un premio que llega solo **al final**, como una voltereta.) ______

**Mi receta de entrenamiento (N2)** — Con lo que has visto, rellena:
| Parámetro | Valor que elegirías | Por qué |
|---|---|---|
| Número de robots (`--env.scene.num-envs`) | | |
| Aprendizaje (`learning-rate`) | | |
| Exploración (`entropy-coef`) | | |
| Rondas (`--agent.max-iterations`) | | |

---

## Extra · ¡A patinar!

**Misión 16 · Patines (N1)** — Abre `exercises/n3_03_patinar.py` y F5. El mismo robot, ahora con ruedas y otro cerebro. **↑** acelera, **← →** giran, **↓** frena, **Espacio** suelta el acelerador. Empújalo con Ctrl + clic derecho mientras rueda.
👀 ¿Qué pasa si aceleras y frenas de golpe? ______ ¿Y si lo empujas de lado? ______
Reto: dibuja un 8 sin caerte.

---

## E · Reto y cierre (opcional, para quien vaya sobrado)

**Reto por parejas** — Usad `exercises/n3_02_marcador.py`: cuenta los segundos de pie y los empujones, y da los PUNTOS (hoja en `PUNTUACION_RETO.md`).
- **A** elige las condiciones para que el robot **falle**; **B**, para que **gane**.

**Mi receta** — Escribe la combinación de opciones que más tira al robot y la que más lo ayuda:

| Quiero… | Opciones | Segundos de pie |
|---|---|---|
| Que **falle** | | |
| Que **gane** | | |

**Una frase para cerrar:** *¿Qué has aprendido sobre por qué es difícil que un robot entrenado en simulador funcione fuera?* ______________________________
