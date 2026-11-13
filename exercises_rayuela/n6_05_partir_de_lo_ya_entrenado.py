"""CURRICULO ENTRE POLITICAS · NO EMPIECES DE CERO: parte de un cerebro que ya sabe algo.

Entrenar un robot desde cero es caro. Lo habitual es ir SUBIENDO: se parte de una politica que ya sabe lo basico (por ejemplo, ANDAR) y se le
ensena lo siguiente (andar por terreno irregular, luchar contra otro robot...). Es un CURRICULO, pero entre politicas en vez de dentro de una.
La guia oficial del proyecto lo dice asi: "elige la plantilla mas cercana y construye sobre ella, no empieces de cero".

EL ARBOL DE POLITICAS QUE SALE DEL ANDAR (datos reales de los ficheros de este repositorio):

                        alpha_walking  (andar con orden de velocidad; unas 10.000 rondas)
          ┌─────────────────────┼──────────────────────────┐
   + terreno irregular    + terreno irregular        + autojuego contra una copia de si mismo
     800 rondas             DESDE CERO, 3.300 rondas   6.000 rondas, desde SU cerebro de andar (checkpoint 10250)
          │                       │                          │
     rough_walk_e            rough_walk_g                 duelo2  (el duelo de la cuerda)

   (La voltereta, en cambio, se entreno de cero: 20.750 rondas. Es otra habilidad, no una variante del andar.)

QUE DICEN LOS DATOS
  · Segun las fichas de sus autores (caidas con bateria, 110 pruebas): alpha_walking 32, rough_walk_e 14 (la mitad), rough_walk_g 12.
    Afinar 800 rondas dio casi lo mismo que entrenar 3.300 desde cero. Y conserva el estilo de andar original: la ficha de g avisa de que, al ser
    un andar completamente nuevo, "el paso al robot real es menos seguro que con las politicas afinadas".
  · En NUESTRO circuito (rampa, escalones, cuadricula, escombros; 6 recorridos por celda; un solo azar, asi que es orientativo):
        nivel 4 (con escombros):  alpha_walking 3 de 6 · rough_walk_e 5 de 6 · rough_walk_g 3 de 6
        niveles 2 y 3 (escalones):  alpha_walking 6 de 6 · rough_walk_e 6 de 6 · rough_walk_g 3 de 6
    Lo puedes repetir tu mismo con n4_06_validar_politicas.py.

LO QUE HACE ESTE EJERCICIO: eliges un CASO y si partes de un cerebro ya entrenado o de cero, y escribe tu paquete de entrenamiento
(mi_entrenamiento/<caso>_curriculo/) con las opciones de mjlab que corresponden. Compara los dos comandos: la diferencia es una linea.

COMO USARLO: ejecuta (F5) tal cual, lee la salida. Despues cambia UN valor, guarda (Ctrl+S) y ejecuta otra vez.
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Que quieres aprender:
#   "obstaculos"  andar por terreno irregular (como el circuito estilo GTC Berlin). Base natural: alpha_walking.
#   "cuerda"      el duelo de la cuerda: dos robots que aprenden jugando entre si. Base natural: el cerebro de andar.
#   "voltereta"   una habilidad nueva: de cero (no hay una politica de andar que se parezca a rodar).
CASO = "obstaculos"

# ¿Partes de un cerebro ya entrenado?
#   AFECTA A: cuantas rondas hacen falta. Desde cero, "obstaculos" necesito 3.300 rondas (rough_walk_g); partiendo de alpha_walking, 800 (rough_walk_e).
#   True  = parte del checkpoint que indiques abajo.   False = empieza con una red al azar.
PARTIR_DE_UNO_YA_ENTRENADO = True

# El checkpoint (.pt) del que partes, el del cerebro de andar. "model_9999.pt" es el que uso el entrenamiento real de rough_walk_e.
#   AFECTA A: lo que ya sabe el robot al empezar: andar. (Pon aqui el tuyo si has entrenado otro.)
CHECKPOINT_BASE = "model_9999.pt"

# Rondas. Con la base: 800 es lo que se uso. Desde cero: 3.300.
#   AFECTA A: lo que cuesta (tiempo de GPU) y lo que aprende.  Prueba 100 partiendo de la base: ¿basta para ver un cambio?
ITERACIONES = None            # None = el valor real del caso (800 con base, 3.300 sin ella; 6.000 en la cuerda)

# Robots a la vez en la GPU. None = el real de cada caso (4096 en obstaculos, 2048 en la cuerda y la voltereta).
NUM_ENVS = None

# ====================================================================

REALES = {   # (con base, sin base) rondas reales, de las fichas de los autores
    "obstaculos": (800, 3300),
    "cuerda": (6000, None),
    "voltereta": (None, 20750),
}


def main():
    import entrenamiento
    if CASO not in REALES:
        raise SystemExit(f"CASO = {CASO!r} no existe. Opciones: {', '.join(REALES)}")
    con_base, sin_base = REALES[CASO]
    if PARTIR_DE_UNO_YA_ENTRENADO and con_base is None:
        print(f"\nOJO: en el caso '{CASO}' no hay un cerebro previo que ayude (es una habilidad distinta). Se prepara DESDE CERO.\n")
    usar_base = PARTIR_DE_UNO_YA_ENTRENADO and con_base is not None
    if not usar_base and sin_base is None:
        print(f"\nOJO: en '{CASO}' no existe un entrenamiento real desde cero con el que comparar; se usan las rondas de la base.\n")
    rondas = ITERACIONES or (con_base if usar_base else (sin_base or con_base))
    print(f"CASO: {CASO} | {'PARTE de ' + CHECKPOINT_BASE if usar_base else 'EMPIEZA DE CERO'} | {rondas} rondas")
    kw = dict(num_envs=NUM_ENVS or {"obstaculos": 4096}.get(CASO, 2048), iteraciones=rondas, guardar_cada=100, nombre=f"taller_{CASO}_curriculo")
    if usar_base and CASO != "cuerda":
        kw["partir_de"] = CHECKPOINT_BASE
    entrenamiento.principal(CASO, destino=AQUI / "mi_entrenamiento" / f"{CASO}_curriculo", **kw)
    if CASO == "cuerda":
        print("\nEn el duelo, la base va por variable de entorno (MICRODUCK_BASE_CHECKPOINT=...model_10250.pt, ver 4_entrenar.sh): lo hacen los parches de patos_cuerda.")
    print("\nPARA PENSAR:")
    print("  · ¿Por que partir de una base cuesta menos? (Ya sabe lo basico, por ejemplo andar: solo aprende lo nuevo. En obstaculos: 800 rondas frente a 3.300.)")
    print("  · ¿Que riesgo tiene? (Hereda sus costumbres, buenas y malas. Y si cambias mucho la tarea, puede 'olvidar' lo anterior.)")
    print("  · ¿Y para el robot real? (rough_walk_g, desde cero, es un andar NUEVO: menos probado que el afinado, que conserva el estilo del original.)")


if __name__ == "__main__":
    main()
