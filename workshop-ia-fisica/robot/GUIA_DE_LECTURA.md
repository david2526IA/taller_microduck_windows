# Cómo leer el modelo del Microduck

Un robot en un simulador se describe en tres capas. Aquí están las tres, para abrirlas en VS Code y leerlas:

```
  PIEZAS (STL)  ──►  EL ROBOT (XML)  ──►  LA ESCENA (XML)
  assets/*.stl       robot_groundcontact.xml     scene.xml
  la forma           cómo se monta y se mueve    el mundo donde está
```

## 1 · Las piezas: `robot/assets/` (43 archivos `.stl`)
Cada pieza es una **malla de triángulos**. Para verlas:
- **Todas a la vez, desmontadas:** `workshop-ia-fisica/exercises/n1_03_despiece.py` (F5).
- **Una sola, con detalle:** `workshop-ia-fisica/exercises/n1_01_ver_pieza.py` (cambia `PIEZA`). Pulsa `W` en el visor para ver los triángulos.

## 2 · El robot: `robot/robot_groundcontact.xml` (434 líneas)
**Para verlo montado y con las articulaciones, los motores y las piezas de colisión dibujados:** `workshop-ia-fisica/exercises/n1_04_robot_por_dentro.py` (F5). También imprime este mismo árbol en la terminal.

Se lee de arriba abajo, y conviene plegar las secciones con las flechas de VS Code.

| Líneas | Qué es | Qué mirar |
|---|---|---|
| 5 | `<compiler>` | `meshdir="assets"`: dónde están los STL |
| 6-58 | `<default>` | Clases reutilizables: cómo se ven las piezas (`visual`) y cómo chocan (`collision`). Y los **motores**: `chosen_actuator` (línea 41) con `kp="0.55"` (lo fuerte que corrige) y `forcerange="-0.96 0.96"` (la fuerza máxima de cada motor) |
| 60 | `<sensor>` | Lo que el robot puede «sentir» |
| 82-337 | `<worldbody>` | **El árbol de piezas.** Empieza en `trunk_base` (línea 84, el tronco) y de él cuelgan las piernas, el cuello y la cabeza, cada una con su `<joint>` (la articulación) |
| 339-416 | `<asset>` | La lista de las 38 `<mesh>`: los STL que se usan |
| 417 | `<actuator>` | Los **14 motores** (uno por articulación: cadera, rodilla, tobillo, cuello, cabeza) |

**Para buscar con `Ctrl+F`:** `trunk_base`, `left_hip_pitch`, `left_knee`, `left_ankle`, `kp=`.
Una articulación se ve así: un `<body>` con un `<joint type="hinge" range="...">` dentro. El `range` es lo que puede girar.

## 3 · La escena: `robot/scene.xml` (62 líneas)
| Líneas | Qué es | Qué cambiar |
|---|---|---|
| 2 | `<include>` | Mete el robot dentro de la escena |
| 4-8 | `<visual>` | La cámara y la luz ambiente |
| 11 | `<texture type="skybox">` | El **cielo**: `rgb1` y `rgb2` son los dos colores (rojo, verde, azul; de 0 a 1) |
| 15 | `<texture name="groundplane">` | El **suelo**: los colores del tablero de ajedrez |
| 19 | `<material>` | `texrepeat="5 5"`: cuántas casillas caben |
| 24 | `<light>` | La luz |
| 27 | `<geom name="floor">` | El suelo físico. `friction=" 1 ..."` es el agarre: 0.1 hielo, 2 goma |
| 29-60 | `<keyframe>` | Posturas guardadas: `STAND` (de pie), `SIT` (sentado), `FOLD` (plegado). Las usa `n1_04` |

Cambia un color, guarda (`Ctrl+S`) y ejecuta `n1_04_robot_por_dentro.py` (F5): lo verás al momento. El archivo ya trae comentarios «CAMBIA ESTO».

## 4 · Cómo encaja con el resto del taller
- Los ejercicios de **mundos** (`n1_02`) cambian la escena **con código**, sin tocar este XML: aquí ves lo mismo escrito a mano.
- Los **cerebros** (`.onnx`) controlan los 14 motores de la lista de `<actuator>`: por eso salen 14 números.
- Origen y licencias de las mallas: [`LICENSE-MODELS.md`](LICENSE-MODELS.md) (CC BY-NC-SA: solo uso no comercial).
