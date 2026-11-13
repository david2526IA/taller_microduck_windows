# Programa del taller · 5 horas (15:00-20:00)

Cada bloque sigue la misma idea: **el ponente explica una cosa (2-5 min) → tú abres un archivo, cambias un parámetro y ves qué pasa**.
Los parámetros están arriba de cada archivo, con comentarios que dicen **en qué afectan**.

**El ciclo de siempre:** abre el archivo en VS Code → cambia **UN** parámetro → `Ctrl+S` → **cierra la ventana del robot** → `F5` → observa.

Las diapositivas: `workshop-ia-fisica/presentaciones/Presentacion_03_taller_completo.pptx` (y `.pdf`).
Los archivos están en dos carpetas: `exercises_rayuela/` (los nuevos) y `workshop-ia-fisica/exercises/` (los de base). Aquí van en orden.

| Hora | Bloque | Dura |
|---|---|---|
| 15:00 | Preparar el PC + Ignición | 20 min |
| 15:20 | **1 · El robot en el simulador** | 35 min |
| 15:55 | **2 · Laboratorio de mundos** | 35 min |
| 16:30 | Descanso | 10 min |
| 16:40 | **3 · El cerebro: RL, política, recompensa** | 40 min |
| 17:20 | **4 · Entrenar** | 55 min |
| 18:15 | Descanso | 10 min |
| 18:25 | **5 · ROS 2 y la partida de la rayuela** | 40 min |
| 19:05 | **6 · De la simulación a la realidad: generalizar** | 35 min |
| 19:40 | Casos de uso + cierre | 20 min |

---

## 1 · El robot en el simulador (35 min)
*Teoría: del plano al gemelo digital: CAD → STL → URDF → MJCF → MuJoCo. Un robot es un árbol de piezas.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `workshop-ia-fisica/exercises/n1_00_ver_robot.py` | `POSE` (STAND, SIT, FOLD) | El robot en distintas posturas; empújalo con Ctrl + clic derecho |
| `workshop-ia-fisica/exercises/n1_01_ver_pieza.py` | La pieza que se muestra | Cada pieza 3D del robot |
| `exercises_rayuela/n0_00_pato_sin_cerebro.py` | `FRICCION`, `FACTOR_MASA`, `EMPUJON`, `VELOCIDAD` | El pato sin IA se cae en menos de 1 s, hagas lo que hagas |

## 2 · Laboratorio de mundos (35 min)
*Teoría: la escena es lo que rodea al robot: suelo, cielo, luz, gravedad, objetos.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `exercises_rayuela/n1_02_tu_escena.py` | `MUNDO` (luna, marte, hielo, desierto, noche), `GRAVEDAD`, `ROZAMIENTO_SUELO`, colores, `OBJETOS` (caja, rampa, esfera, cilindro) | El mismo pato en mundos distintos; la pelota vuela en la Luna; un laberinto de cajas |
| `exercises_rayuela/n4_05_obstaculos.py` | `NIVEL` 0→4, `CEREBRO`, alturas | Un circuito en crescendo: rampa, escalones, cuadrícula irregular, escombros |

## 3 · El cerebro: RL, política, recompensa (40 min)
*Teoría: aprender es como montar en bici; el bucle agente-entorno; la red neuronal es una función con botones; recompensa; PPO.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `workshop-ia-fisica/exercises/n3_00_demo_con_cerebro.py` | Las teclas (andar, `Y` sentarse, `R` voltereta) | El mismo robot, ahora con IA: anda y se recupera de empujones |
| `workshop-ia-fisica/exercises/n2_03_dentro_del_cerebro.py` | `CEREBRO` (recién nacido, tambaleante, mejor, andar) | Qué es una **política**: 61 números entran, 14 salen, en vivo |
| `workshop-ia-fisica/exercises/n2_00_cerebro_en_vivo.py` | `QUITAR_SENTIDO`, `RUIDO_SENTIDOS`, `RUIDO_ORDENES` | Le quitas un sentido al cerebro (inclinación, giro...) o le metes ruido: ¿qué es lo que más necesita? |
| `workshop-ia-fisica/exercises/n2_01_recompensa_en_vivo.py` | Los pesos de la recompensa | La nota del pato mientras lo empujas |

## 4 · Entrenar (55 min)
*Teoría: el ciclo del entrenamiento, los botones (learning rate, exploración, rondas), PPO de verdad.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `workshop-ia-fisica/exercises/n3_01_progresion.py` | `NIVEL` 0→5 | El mismo robot recién nacido, a medio entrenar y ya bueno |
| `workshop-ia-fisica/exercises/n3_04_curvas_entrenamiento.py` | Qué parámetro se cambió | Curvas reales de entrenamiento: predices y compruebas |
| `exercises_rayuela/n3_05_entrena_la_patada.py` | Recompensa, `LEARNING_RATE`, `EXPLORACION`, `ITERACIONES`, `CASILLAS`… | **PPO real en tu PC (~3 min):** la curva sube y pasas de ~1 a ~8 aciertos de 9 |
| `exercises_rayuela/n3_06_comparar_politicas.py` | Qué políticas comparas | Tu política frente a otras y frente a la oficial |

## 5 · ROS 2 y la partida de la rayuela (40 min)
*Teoría: una política es un fichero .onnx; nodos, topics y lanzadores; cómo encajan visión, control y teleoperación.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `exercises_rayuela/n4_01_ros2_en_vivo.py` | — | Los nodos y topics de la Rayuela oficial funcionando |
| `exercises_rayuela/n4_00_partida_rayuela.py` | `TABLA_PROPIA`, `OBJETIVO`, `PUNTOS` | La partida con **tu** política: patada, visión y marcador |

## 6 · De la simulación a la realidad: generalizar (35 min)
*Teoría: la brecha sim-to-real; aleatorización de dominio; la lista antes de llevar una política al robot.*

| Archivo | Qué cambias | Qué ves |
|---|---|---|
| `exercises_rayuela/n5_01_generalizar.py` | `MUNDOS_PRUEBA`, `POLITICAS` | Se ejecuta ya (trae 3 políticas de ejemplo): una tabla de cuál aguanta cuando el mundo cambia. Medido: entrenada en un solo mundo, 8/9 y se hunde (4,2 de media); a ciegas con mundos al azar, peor (2,0); **percibiendo el mundo, 8/9 y aguanta (6,8)** |
| `exercises_rayuela/n3_05_entrena_la_patada.py` | `ALEATORIZAR` (0 = un solo mundo, 0.25 = mundos al azar), `VE_EL_MUNDO`, `ITERACIONES` (150), `NOMBRE_POLITICA` | Entrenas la tuya (~6 min en segundo plano) y la añades a la tabla |
| `workshop-ia-fisica/exercises/n3_00_demo_con_cerebro.py` | `VOLTAJE_BATERIA` (6.5 = batería baja), `RETRASO_MOTORES` | Los fallos típicos del robot real, simulados: batería baja, motores que obedecen tarde |
| `exercises_rayuela/n5_00_preparar_sim2real.py` | Nivel de dificultad | El contrato del .onnx y la robustez en crescendo |

## Casos de uso + cierre (20 min): elige uno
| Archivo | Qué es |
|---|---|
| `exercises_rayuela/n4_02_patines.py` | El Microduck con ruedas |
| `exercises_rayuela/n4_03_cuerda.py` | El duelo de la cuerda: dos patos, una cuerda |
| `exercises_rayuela/n4_04_equilibrio.py` | Empújalo y se corrige; pruébalo sobre un balancín |
| `exercises_rayuela/n4_06_validar_politicas.py` | Mide con números los cerebros en el circuito |

---

**Sin editar archivos:** `MJLAB.bat` abre `mini_mjlab`, con los mismos verbos que mjlab pero en CPU
(`MJLAB list-envs`, `MJLAB params <entorno>`, `MJLAB play ...`, `MJLAB train ...`).

**Si algo falla:** envía `instalar_log.txt` al ponente; mira la tabla de problemas del [`README.md`](README.md).
