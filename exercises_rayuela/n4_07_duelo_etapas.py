"""CASO DE USO 3b - ¿MAS ENTRENADO ES MEJOR? Las etapas del duelo de la cuerda, medidas.

Durante el entrenamiento se guardan copias del cerebro (checkpoints). Aqui tienes nueve de una sola carrera de 6.027 iteraciones.
Este ejercicio hace combatir a la etapa que elijas (pato A) contra un rival y cuenta victorias, derrotas y caidas.
Sin ventana: tarda unos segundos por combate en tu CPU. Es la misma idea que n3_08 (medir la voltereta): se guarda, se MIDE y se elige.

EXPERIMENTOS: cambia UN valor, guarda (Ctrl+S) y lanza otra vez (F5).
"""
import pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Etapas que quieres medir (cada una juega de pato A). Disponibles: 0, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6027.
#   AFECTA A: cuantas filas tiene la tabla y cuanto tarda (unos 5-10 s por combate). Prueba [1000, 6027] para ir rapido.
ETAPAS = [0, 1000, 3000, 6027]

# Rival (pato B): "ANDA" = el cerebro de andar sin entrenar para el duelo | un numero de etapa, por ejemplo 6027.
#   AFECTA A: contra quien se mide. Contra "ANDA" casi todas las etapas ganan menos la final; contra 6027 gana casi cualquiera.
RIVAL = "ANDA"

# Combates por etapa. Mas combates = medida mas fiable, pero mas lenta.
#   AFECTA A: la fiabilidad. Con 4 el resultado cambia de una vez a otra; con 12 ya se parece a lo que ensenamos en la presentacion.
COMBATES = 6

# Semilla del azar (el mismo numero repite exactamente los mismos combates).
#   AFECTA A: que combates salen. Cambiala para comprobar que la conclusion no depende de la suerte.
SEMILLA = 4

# ====================================================================

if __name__ == "__main__":
    import contextlib, io, duelo
    carpeta = AQUI / "windows" / "politicas" / "duelo"
    prueba = "--prueba" in sys.argv
    etapas = [6027] if prueba else ETAPAS
    n = 1 if prueba else COMBATES
    print(f"{'etapa':>6s} | gana / pierde / empata | caidas")
    for e in etapas:
        kw = dict(b_solo_anda=True) if RIVAL == "ANDA" else dict(politica_b=carpeta / f"duelo_{int(RIVAL):05d}.onnx")
        with contextlib.redirect_stdout(io.StringIO()):
            r = duelo.lanzar_duelo(politica_a=carpeta / f"duelo_{e:05d}.onnx", combates=n, visor=False, semilla=SEMILLA, verbose=False,
                                   segundos=3000, desplazamiento=0.05, **kw)
        print(f"{e:6d} | {r['A']:5d} / {r['B']:5d} / {r['empates']:5d} | {r['caidas']:5d}", flush=True)
    print("\nLeelo asi: si una etapa gana mas que la final, 'mas entrenado' no ha sido 'mejor'. Por eso se guardan checkpoints y se mide.")
