# El proyecto base: el robot, los cerebros y los ejercicios

Aquí vive todo lo que usa el taller con el **Microduck** (Pollen Robotics) en **MuJoCo**, en un PC sin GPU.
**El orden del taller está en [`PROGRAMA.md`](../PROGRAMA.md)** (en la raíz del repositorio).

```
workshop-ia-fisica/
├── robot/        el CUERPO: las piezas 3D (assets/*.stl), el robot en XML y la escena. Empieza por GUIA_DE_LECTURA.md
├── policies/     el CEREBRO: redes neuronales ya entrenadas (.onnx), incluidos los 9 checkpoints de la voltereta
├── exercises/    los ejercicios de esta carpeta (lista abajo)
├── scripts/      infer_policy.py: pone a un cerebro a manejar el cuerpo
├── entrenar/     cómo se ENTRENA de verdad (GPU NVIDIA): scripts explicados y curvas reales
├── wheels/       las librerías para instalar sin internet
└── presentaciones/   las diapositivas del taller
```

## Los ejercicios de esta carpeta
Se ejecutan con **F5** (con el archivo abierto). Arriba de cada uno están los parámetros, y cada uno dice en qué afecta.

| Archivo | Qué hace |
|---|---|
| `n1_01_ver_pieza.py` | Una pieza 3D suelta |
| `n1_03_despiece.py` | Las 43 piezas 3D, en cuadrícula |
| `n1_04_robot_por_dentro.py` | El robot montado, con articulaciones, motores y colisiones dibujados |
| `n2_00_cerebro_en_vivo.py` | Le quitas un sentido al cerebro o le metes ruido |
| `n2_01_recompensa_en_vivo.py` | La recompensa del pato, en vivo |
| `n2_03_dentro_del_cerebro.py` | Qué entra y qué sale de una política |
| `n3_00_demo_con_cerebro.py` | El robot con IA: andar, sentarse, voltereta; batería baja y retrasos |
| `n3_04_curvas_entrenamiento.py` | Curvas reales de entrenamiento |
| `n3_07_voltereta_checkpoints.py` | La voltereta en nueve momentos de un entrenamiento real |
| `n3_08_voltereta_medir.py` | Mide cada checkpoint con números |

Origen y licencias: [`ORIGEN.md`](../ORIGEN.md) (las mallas 3D son CC BY-NC-SA: solo uso no comercial).
