"""LA RUTA GUIADA DEL TALLER: del pato que se cae al pato que juega a la rayuela.

Un solo programa que te lleva paso a paso. En cada paso lee QUE VAS A VER y PARA QUE SIRVE, pulsa Enter para
lanzarlo, cierra la ventana del robot cuando hayas visto lo que toca, y vuelves aqui para el siguiente.
Puedes saltarte pasos (s) o salir (q) y retomarlo cuando quieras.   Doble clic en RUTA.bat para empezar.
"""
import pathlib, subprocess, sys

for _f in (sys.stdout, sys.stderr):      # tildes y simbolos bien en la consola de Windows
    _f.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parent
PY = RAIZ / "workshop-ia-fisica" / ".venv" / "Scripts" / "python.exe"
EJ = RAIZ / "exercises_rayuela"
TALLER = RAIZ / "workshop-ia-fisica" / "exercises"

PASOS = [
    ("1 · TU ENTORNO", "Comprobar que el ordenador esta listo",
     "Python 3.12, un entorno virtual (.venv) con las librerias exactas, el simulador MuJoCo y los cerebros (.onnx).",
     "Una lista de [ OK ] que acaba en TODO LISTO y el robot en el visor 5 segundos.",
     "Que un proyecto de robotica son piezas con versiones fijas; si todas dicen OK, todo lo demas funciona igual en todos los PCs.",
     [PY, RAIZ / "workshop-ia-fisica" / "check_setup.py", "--viewer"]),

    ("2 · EL PATO SIN CEREBRO", "Ver como se cae",
     "Le ordenamos al robot 'mantén la postura de pie' con un control simple, sin IA.",
     "El pato se cae en menos de un segundo (esta en camara lenta). En la terminal sale cuanto aguanto.",
     "Equilibrar dos patas no se resuelve con una postura fija: hay que reaccionar 50 veces por segundo. Eso es lo que hara la IA.",
     [PY, EJ / "n0_00_pato_sin_cerebro.py"]),

    ("3 · METERLE IA", "El mismo pato, ahora con cerebro",
     "Cargamos una red neuronal entrenada (un fichero .onnx) que recibe lo que siente el robot y decide los 14 motores.",
     "El pato anda, se sienta, rueda y se recupera de empujones. Teclas en la TERMINAL: flechas, Y (sentarse), R (voltereta). "
     "Empujalo con Ctrl + clic derecho.",
     "Que el cerebro es una funcion: entran numeros, salen ordenes. Nadie escribio reglas para andar.",
     [PY, TALLER / "n3_00_demo_con_cerebro.py"]),

    ("4 · DENTRO DEL CEREBRO", "Que siente y que ordena, en vivo",
     "La misma red, pero mostrando sus 61 entradas (lo que siente) y 14 salidas (lo que ordena).",
     "Un panel con barras que cambian mientras andas. Prueba con las flechas y empuja al pato.",
     "Observacion -> cerebro -> accion: el bucle de todo el RL. Y a que sentidos hace mas caso.",
     [PY, TALLER / "n2_00_cerebro_en_vivo.py"]),

    ("5 · COMO SE LE PUNTUA", "La recompensa",
     "El aprendizaje por refuerzo premia o castiga con una suma de piezas por pesos (altura, verticalidad, avanzar, esfuerzo).",
     "Una tabla con la nota del pato en cada instante. Casi se cae = la nota baja.",
     "Que disenar la recompensa es la parte dificil: el robot hace exactamente lo que se premia, no lo que querias.",
     [PY, TALLER / "n2_01_recompensa_en_vivo.py"]),

    ("6 · ENTRENAR", "PPO de verdad, en tu PC (unos 2 minutos)",
     "Entrenamos una politica que decide COMO patear la pelota para que caiga en cada casilla de la rayuela: prueba, puntua, ajusta, repite.",
     "Una curva que sube (la recompensa) y una tabla ANTES / DESPUES: pasa de ~1 a ~6 aciertos de 9.",
     "El bucle completo del RL con PPO. Despues cambia UN parametro del fichero (n3_05) y repite: asi se aprende que hace cada boton.",
     [PY, EJ / "n3_05_entrena_la_patada.py"]),

    ("7 · EL RESULTADO", "La partida de la rayuela con TU politica",
     "Visión, control y teleoperacion (ROS 2 en miniatura) integran lo entrenado: patea, la camara ve donde cae, el pato va a la casilla.",
     "Una ronda con marcador. Teclas 1-9 = patada a esa casilla con TU politica; k/l = patada a tu velocidad; h = a casa; n = ronda nueva.",
     "Como se integra todo: simulacion + cerebro + vision + control. Es el resultado del taller.",
     [PY, EJ / "n4_00_partida_rayuela.py"]),
]

EXTRAS = [
    ("a", "Patines: otro cuerpo y otro cerebro", EJ / "n4_02_patines.py"),
    ("b", "La cuerda: dos patos tirando", EJ / "n4_03_cuerda.py"),
    ("c", "El equilibrio: tu lo empujas y el se autocorrige", EJ / "n4_04_equilibrio.py"),
    ("d", "El circuito de obstaculos (GTC Berlin): rampa, escalones, cuadricula, escombros", EJ / "n4_05_obstaculos.py"),
    ("f", "Validar cerebros en el circuito, con numeros", EJ / "n4_06_validar_politicas.py"),
    ("g", "ROS 2 en vivo: nodos y topics", EJ / "n4_01_ros2_en_vivo.py"),
    ("e", "Tu propia escena: gravedad, rozamiento, obstaculos", EJ / "n1_02_tu_escena.py"),
]


def lanzar(cmd):
    print("\n   >>> se abre; cierra la ventana del robot (o pulsa q en la terminal) para volver aqui\n")
    try:
        subprocess.run([str(c) for c in cmd], cwd=str(RAIZ))
    except KeyboardInterrupt:
        pass


def main():
    if not PY.exists():
        sys.exit("Falta el entorno. Haz doble clic en INSTALAR.bat primero.")
    print(__doc__)
    for titulo, subtitulo, que, ver, aprende, cmd in PASOS:
        print("=" * 78 + f"\n PASO {titulo}: {subtitulo}\n" + "=" * 78)
        print(f" QUE VAS A HACER : {que}\n QUE VAS A VER   : {ver}\n QUE SE APRENDE  : {aprende}\n")
        r = input(" [Enter] lanzar   [s] saltar   [q] salir > ").strip().lower()
        if r == "q":
            return
        if r != "s":
            lanzar(cmd)
            input("\n Hecho. [Enter] para el siguiente paso > ")
    print("=" * 78 + "\n CASOS DE USO: lo mismo, con otros cuerpos y otros mundos\n" + "=" * 78)
    while True:
        for k, nombre, _ in EXTRAS:
            print(f"   [{k}] {nombre}")
        r = input(" Elige una letra para lanzarlo, o [q] para terminar > ").strip().lower()
        if r == "q":
            break
        for k, _, ruta in EXTRAS:
            if r == k:
                lanzar([PY, ruta])
    print("\nFin de la ruta. Cada ejercicio tiene parametros arriba: cambia UNO, guarda, cierra la ventana y lanza otra vez.")


if __name__ == "__main__":
    main()
