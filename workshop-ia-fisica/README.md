# IA aplicada a un entorno físico

Taller en simulación con **Microduck**, un robot bípedo open source de Pollen Robotics, en el simulador **MuJoCo**.
No hace falta robot ni GPU (entrenar un cerebro propio sí la necesita: ver [`entrenar/ENTRENAR.md`](entrenar/ENTRENAR.md)). 👉 **Empieza por [`TALLER.md`](TALLER.md).**

## Cómo empezar (3 minutos)

1. Abre esta carpeta en VS Code.
2. Haz **doble clic en `INSTALAR.bat`** (instala todo sin internet).
3. Haz **doble clic en `COMPROBAR.bat`**: debe acabar en **TODO LISTO** y mostrar el robot.
4. Abre [`TALLER.md`](TALLER.md) y sigue los bloques. El orden: laboratorio → gemelo digital → cerebro → laboratorio con IA → realidad.

**El ciclo de trabajo de todo el taller:** abre el ejercicio → cambia UN valor → guarda (Ctrl+S) y **cierra la ventana del robot** → lánzalo otra vez y observa.

## Qué hay aquí

```
workshop-ia-fisica/
├── TALLER.md            ← la guía por bloques, con qué observar y qué pensar
├── MISIONES.md          ← 16 misiones cortas para anotar lo que ves
├── PUNTUACION_RETO.md   ← hoja del reto por parejas (opcional)
├── robot/               ← el CUERPO: modelo 3D y física del robot
├── policies/            ← el CEREBRO: redes neuronales ya entrenadas (.onnx)
├── exercises/           ← tus ejercicios (n1 = solo mirar · n2 = tocar valores · n3 = laboratorio con IA)
├── entrenar/            ← cómo se ENTRENA un cerebro (GPU NVIDIA): scripts explicados + guía
├── scripts/
│   └── infer_policy.py  ← pone a un cerebro a manejar el cuerpo
├── presentaciones/      ← las diapositivas del taller
├── INSTALAR.bat         ← prepara tu PC (doble clic, una vez)
├── COMPROBAR.bat        ← comprueba que todo funciona
├── run_demo.bat         ← demo con todas las habilidades (doble clic)
├── run_reto.bat         ← la demo lista para el reto (opcional)
├── run_ver_robot.bat    ← abre el robot en el visor (doble clic)
├── check_setup.py       ← el programa de la comprobación
├── requirements.txt     ← lista de librerías de Python
└── wheels/              ← las librerías ya descargadas (para instalar sin internet)
```

## Los comandos que importan

Abre la carpeta en VS Code y, en su terminal (`Terminal → New Terminal`):

| Quiero… | Comando |
|---|---|
| Comprobar que todo funciona | `python check_setup.py --viewer` |
| Ver el robot | `python exercises/n1_00_ver_robot.py` |
| Verlo andar con IA | `run_demo.bat` (en Linux: `python exercises/n3_00_demo_con_cerebro.py`) |
| Verlo patinar | `python exercises/n3_03_patinar.py` |
| Jugar al reto con marcador | `python exercises/n3_02_marcador.py` |

## Controles de la demo
Se pulsan **en la terminal**, no en la ventana del robot.

| Tecla | Acción | | Tecla | Acción |
|---|---|---|---|---|
| ↑ ↓ | adelante / atrás | | `Y` | sentarse / levantarse |
| ← → | lado | | `R` | voltereta |
| `A` / `E` | girar | | Espacio | parar |
| `Q` | salir | | | |

En el visor: **Ctrl + clic derecho arrastrando = empujar al robot**.

## Créditos y licencias
- Robot y políticas: [Pollen Robotics](https://github.com/pollen-robotics/microduck_rl) (código Apache-2.0).
- Mallas 3D (`robot/assets/`): CC BY-NC-SA 4.0 — solo uso **no comercial** (ver `robot/LICENSE-MODELS.md`).
- `scripts/infer_policy.py` adaptado para Windows; original Apache-2.0.
