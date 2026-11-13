# Glosario: las palabras del taller, sin jerga

Para cualquier nivel. Si una palabra del código o de las diapositivas no la conoces, búscala aquí.

| Palabra | Qué es, en una frase | Ejemplo del taller |
|---|---|---|
| **Simulador** (MuJoCo) | Un programa que calcula la física (gravedad, choques, motores) como si el robot fuera real | La ventana donde ves al pato |
| **Gemelo digital** | El robot en el ordenador, con la misma forma y peso que el real | El Microduck del simulador |
| **Escena** | Todo lo que rodea al robot: suelo, cielo, luz, objetos | `n1_02`: cambias gravedad, colores y objetos |
| **Entorno** | El "juego" del robot: el mundo + lo que ve + lo que puede hacer + cómo se le puntúa | La patada a una casilla |
| **Observación** | Lo que el robot **siente** en cada instante (inclinación, giro, posición de los motores...) | Los 61 números que entran al cerebro |
| **Acción** | Lo que el robot **ordena** a sus motores | Los 14 números que salen del cerebro |
| **Recompensa** | La **nota** que recibe el robot en cada paso: puntos por lo que está bien, castigo por lo que está mal | Piezas × pesos, `n2_01` |
| **Peso** | Cuánto cuenta cada pieza de la recompensa | `roulade_progress = 8.0` |
| **Política** (cerebro) | La función que, viendo la observación, decide la acción. Una red neuronal | Cada fichero `.onnx` |
| **Red neuronal** | Una función con muchos "botones" (números) que se ajustan al aprender | 197.896 números en el cerebro de andar |
| **RL** (aprendizaje por refuerzo) | Aprender por ensayo y error, guiado solo por la recompensa | Todo el taller |
| **PPO** | El algoritmo que ajusta el cerebro con pasos pequeños, para no estropear lo ya aprendido | `n3_05` lo implementa de verdad |
| **Episodio** | Un intento completo, desde que empieza hasta que acaba o se cae | Una patada, una voltereta (5 s) |
| **Ronda** (iteración) | Un ciclo de "probar muchas veces, puntuar y ajustar el cerebro" | "Entrenado 750 rondas" |
| **Checkpoint** | Una copia del cerebro guardada durante el entrenamiento. Como una foto de un álbum | `n3_07`: 9 checkpoints de la voltereta |
| **Curva de aprendizaje** | La recompensa media según avanzan las rondas. Si sube, el robot aprende | `n3_08` |
| **Exploración** | Cuánto prueba cosas raras mientras aprende | `EXPLORACION` en `n3_05` |
| **Tasa de aprendizaje** | Lo grande que es cada ajuste del cerebro. Muy alta: se descontrola. Muy baja: no aprende | `LEARNING_RATE` |
| **Gamma** | Cuánto "piensa en el futuro" el robot (0,8 = miope; 0,99 = largo plazo) | `GAMMA` |
| **Robots a la vez** (`num-envs`) | Cuántas simulaciones entrenan en paralelo en la GPU. Más = más experiencia por minuto | 2048 en la voltereta |
| **GPU** | La tarjeta gráfica; hace miles de cálculos a la vez. El entrenamiento real la necesita | No la tenemos en el taller |
| **mjlab** | La herramienta real con la que se entrena el Microduck (MuJoCo en GPU) | `n6_*` prepara su configuración |
| **Currículo** | Empezar fácil y subir la dificultad (o los pesos) según el robot mejora | El terreno del circuito; los pesos de la patada |
| **ONNX** (`.onnx`) | El formato de fichero en el que se guarda un cerebro entrenado, para usarlo sin la GPU | `alpha_walking.onnx` |
| **Sim-to-real** | Llevar lo aprendido en simulación al robot de verdad | `n5_00` y `n5_01` |
| **Brecha sim-to-real** | La diferencia entre el robot simulado y el real: nunca son idénticos | Otro suelo, otra masa, otra pelota |
| **Aleatorización de dominio** | Entrenar en mundos distintos al azar para que el cerebro aguante los cambios | `ALEATORIZAR` en `n3_05` |
| **ROS 2** | El "sistema de tuberías" de los robots: programas (nodos) que se hablan por canales (topics) | `n4_01` |
| **Nodo / topic / launch** | Un programa pequeño / un canal por donde se mandan mensajes / el fichero que arranca todos | Visión, control y teleoperación de la Rayuela |
| **Prueba de humo** | Lanzar un entrenamiento minúsculo (64 robots, 5 rondas) para ver que no falla, antes del largo | `3_probar.sh` de tu paquete |
