# Programa del taller · 5 horas (15:00-20:00)

## La idea del taller en una frase
Un robot pequeño (el Microduck) **aprende una habilidad por ensayo y error**. Recorremos el camino completo, con las manos en el código:

```
  MODELAR el robot  →  crear el ENTORNO  →  ENTRENAR (RL)  →  DESPLEGAR (sim-to-real)
        └────────────────── y vuelta atrás: casi nunca sale a la primera ──────────────────┘
```

Cada bloque es una parte de ese camino. Y **entender cada paso** importa porque, cuando algo falla, sabes qué tocar.

## Cómo se trabaja (siempre igual)
1. El ponente explica una idea (2-5 minutos).
2. Tú abres **un archivo**, cambias **UN número** de los de arriba (cada uno dice en qué afecta), guardas (`Ctrl+S`).
3. **Cierras la ventana del robot** (si hay) y lo ejecutas otra vez con `F5`. Miras qué ha cambiado.

Los archivos están en dos carpetas: `workshop-ia-fisica/exercises/` (la serie base, `n1` a `n3`) y `exercises_rayuela/` (el resto).
Las diapositivas: `workshop-ia-fisica/presentaciones/Presentacion_03_taller_completo.pptx` (y `.pdf`).
Si una palabra no la conoces, está en [`GLOSARIO.md`](GLOSARIO.md).

## El mapa de horas

| Hora | Bloque | Min |
|---|---|---|
| 15:00 | Preparar el PC + ignición | 20 |
| 15:20 | **1 · El robot en el simulador** (modelar) | 30 |
| 15:50 | **2 · Laboratorio de mundos** | 35 |
| 16:25 | Descanso | 10 |
| 16:35 | **3 · El cerebro y la recompensa** (RL, política, PPO) | 40 |
| 17:15 | **4 · La voltereta: de cero a experto** (entrenar) | 55 |
| 18:10 | Descanso | 10 |
| 18:20 | **5 · Configura tu entrenamiento real** | 35 |
| 18:55 | **6 · ROS 2 y la partida de la rayuela** | 35 |
| 19:30 | **7 · Sim-to-real** y cierre | 30 |

---

## 1 · El robot en el simulador (30 min) · *modelar*
*Teoría: del plano al gemelo digital: modelo 3D → STL → URDF → MJCF → MuJoCo. Un robot es un árbol de piezas con articulaciones.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `workshop-ia-fisica/exercises/n1_00_ver_robot.py` | `POSE` (STAND, SIT, FOLD) | El robot en distintas posturas; empújalo con Ctrl + clic derecho |
| `workshop-ia-fisica/exercises/n1_01_ver_pieza.py` | `PIEZA` | Cada pieza 3D del robot |
| `exercises_rayuela/n0_00_pato_sin_cerebro.py` | `FRICCION`, `FACTOR_MASA`, `EMPUJON`, `VELOCIDAD` | El pato sin IA se cae en menos de 1 s, hagas lo que hagas |

## 2 · Laboratorio de mundos (35 min) · *el entorno: el mundo*
*Teoría: la escena es lo que rodea al robot: suelo, cielo, luz, gravedad, objetos.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `exercises_rayuela/n1_02_tu_escena.py` | `MUNDO` (luna, marte, hielo, desierto, noche), gravedad, rozamiento, colores, `OBJETOS` (caja, rampa, esfera, cilindro) | El mismo pato en mundos distintos; la pelota vuela en la Luna; un laberinto de cajas |
| `exercises_rayuela/n4_05_obstaculos.py` | `NIVEL` de 0 a 4, `CEREBRO` | Un circuito en crescendo: rampa, escalones, cuadrícula irregular, escombros |

## 3 · El cerebro y la recompensa (40 min) · *el entorno: qué se ve, qué se hace, qué se premia*
*Teoría: aprender es como montar en bici; el bucle agente-entorno; la red neuronal es una función con botones; la recompensa; PPO.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `workshop-ia-fisica/exercises/n3_00_demo_con_cerebro.py` | Las teclas (andar, `Y` sentarse, `R` voltereta) | El mismo robot, ahora con IA: anda y se recupera de empujones |
| `workshop-ia-fisica/exercises/n2_03_dentro_del_cerebro.py` | `CEREBRO` | Qué es una **política**: 61 números entran, 14 salen, en vivo |
| `workshop-ia-fisica/exercises/n2_00_cerebro_en_vivo.py` | `QUITAR_SENTIDO`, `RUIDO_SENTIDOS`, `RUIDO_ORDENES` | Le quitas un sentido al cerebro o le metes ruido: ¿qué es lo que más necesita? |
| `workshop-ia-fisica/exercises/n2_01_recompensa_en_vivo.py` | Los pesos de la recompensa | La nota del pato mientras lo empujas |

## 4 · La voltereta: de cero a experto (55 min) · *entrenar*
*Teoría: el ciclo del entrenamiento; checkpoints; los botones del entrenamiento (rondas, robots a la vez, tasa de aprendizaje, exploración); PPO de verdad.*
La voltereta es **una habilidad sencilla de describir** y difícil de aprender. Hay nueve **checkpoints** (copias del cerebro guardadas durante un entrenamiento real de 20.750 rondas).

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `workshop-ia-fisica/exercises/n3_07_voltereta_checkpoints.py` | `CHECKPOINT` (0, 500, 750, 1250, 3000, 7000, 11000, 20000, 20750) | El mismo robot en distintos momentos de su aprendizaje: pulsa `R` para la voltereta |
| `workshop-ia-fisica/exercises/n3_08_voltereta_medir.py` | `CHECKPOINTS`, `INTENTOS` | Una tabla con números y la curva real. Medido: aparece a las 750 rondas, se vuelve irregular, se estabiliza hacia las 11.000, y **el 20.000 es peor que el 11.000** |
| `workshop-ia-fisica/exercises/n3_04_curvas_entrenamiento.py` | Qué parámetro se cambió | Curvas reales: predices y compruebas |
| `exercises_rayuela/n3_05_entrena_la_patada.py` | Recompensa, `LEARNING_RATE`, `EXPLORACION`, `ITERACIONES`, `CASILLAS`… | **Entrenas tú, de verdad, en tu CPU (~3 min):** PPO sobre la patada; la curva sube de ~1 a ~8 aciertos de 9 |
| `exercises_rayuela/n3_06_comparar_politicas.py` | Qué políticas comparas | Tu política frente a otras y frente a la oficial |

## 5 · Configura tu entrenamiento real (35 min) · *lo que se hace antes de pulsar "entrenar"*
*Teoría: mjlab, la herramienta real; una tarea = escena + observaciones + acciones + recompensa + algoritmo; GPU local o en la nube.*
Sin GPU no se puede entrenar con mjlab, pero **todo lo anterior al botón sí se prepara**. Cada ejercicio lee la configuración oficial, te deja cambiarla y escribe **tu paquete** (`mi_entrenamiento/<caso>/`) listo para lanzar en un PC con GPU o en la nube.

| Archivo | Caso |
|---|---|
| `exercises_rayuela/n6_00_entrenar_voltereta.py` | **La voltereta** (el caso de partida, con los valores del entrenamiento real) |
| `exercises_rayuela/n6_01_entrenar_rayuela.py` | La Rayuela: patear a una casilla |
| `exercises_rayuela/n6_02_entrenar_cuerda.py` | El duelo de la cuerda (autojuego) |
| `exercises_rayuela/n6_03_entrenar_patines.py` | Los patines: otro cuerpo |
| `exercises_rayuela/n6_04_entrenar_obstaculos.py` | Obstáculos (GTC): terreno irregular |

Haz el 00 entero; de los otros cuatro, elige uno. Lo que se hace en todos: **elegir la tarea → leer la recompensa real → cambiar un peso → generar el paquete → leer el comando**.

## 6 · ROS 2 y la partida de la rayuela (35 min) · *desplegar la política*
*Teoría: una política es un fichero .onnx; nodos, topics y lanzadores; cómo encajan visión, control y teleoperación.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `exercises_rayuela/n4_01_ros2_en_vivo.py` | `VISION`, `CONTROL` | Los nodos y topics de la Rayuela oficial funcionando |
| `exercises_rayuela/n4_00_partida_rayuela.py` | `TABLA_PROPIA`, `OBJETIVO`, `PUNTOS` | La partida con **tu** política: patada, visión y marcador |

## 7 · Sim-to-real (30 min, con el cierre) · *la brecha y cómo se cierra*
*Teoría: la brecha entre simulación y realidad; aleatorización de dominio; la lista antes de llevar una política al robot.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `exercises_rayuela/n5_01_generalizar.py` | `MUNDOS_PRUEBA`, `POLITICAS` | Se ejecuta ya (trae 3 políticas de ejemplo). Medido: entrenada en un solo mundo, 8/9 y se hunde (4,2 de media); con mundos al azar **a ciegas**, peor (2,0); **percibiendo el mundo, 8/9 y aguanta (6,8)** |
| `workshop-ia-fisica/exercises/n3_00_demo_con_cerebro.py` | `VOLTAJE_BATERIA` (6.5), `RETRASO_MOTORES` | Fallos típicos del robot real, simulados: batería baja, motores que obedecen tarde |
| `exercises_rayuela/n5_00_preparar_sim2real.py` | Nivel de dificultad | El contrato del .onnx y la robustez en crescendo |

## Casos de uso (para casa, o si sobra tiempo)
| Archivo | Qué es |
|---|---|
| `exercises_rayuela/n4_02_patines.py` | El Microduck con ruedas |
| `exercises_rayuela/n4_03_cuerda.py` | El duelo de la cuerda: dos patos, una cuerda |
| `exercises_rayuela/n4_04_equilibrio.py` | Empújalo y se corrige; pruébalo sobre un balancín |
| `exercises_rayuela/n4_06_validar_politicas.py` | Mide con números los cerebros en el circuito |

---

**Sin editar archivos:** `MJLAB.bat` abre `mini_mjlab`, con los mismos verbos que mjlab pero en CPU (`MJLAB list-envs`, `MJLAB params <entorno>`, `MJLAB play ...`, `MJLAB train ...`).

**Si algo falla:** envía `instalar_log.txt` al ponente; mira la tabla de problemas del [`README.md`](README.md).

**Si no tienes el PC a mano:** todo el taller se sigue con las diapositivas; los números medidos están en las notas de cada una.
