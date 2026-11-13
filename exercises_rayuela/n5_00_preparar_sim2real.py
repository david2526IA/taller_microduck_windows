"""NIVEL 5 - PREPARA EL SIM-TO-REAL: ¿esta lista tu politica para llevarla a un robot de verdad?

Una politica que anda de maravilla en simulacion puede caerse en el robot real: la brecha sim-to-real. La receta para cerrarla no
es magia, es una lista de comprobaciones que haces ANTES de arriesgar el hardware:
  1. CONTRATO: ¿el .onnx tiene la forma que espera el robot? (61 entradas, 14 salidas, 32 bits, 64 MiB como maximo)
  2. ROBUSTEZ EN CRESCENDO (aleatorizacion del dominio): la pruebas con un mundo cada vez mas "sucio" y cuentas caidas.
        0 mundo ideal | 1 + rozamiento al azar | 2 + masa al azar | 3 + bateria baja | 4 + retraso en los motores | 5 + empujones
  3. LISTA de despliegue: como copiarla al robot y como volver atras.
Todo en simulacion y en tu CPU (unos 2-3 minutos con los valores por defecto). No hay robot: esto es la preparacion, no la prueba final.

EXPERIMENTOS: cambia UN valor, guarda (Ctrl+S) y ejecuta (F5). Mira en que nivel empiezan las caidas de cada cerebro.
"""
import pathlib, sys, time

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))

# ============================ PARAMETROS ============================

# Los cerebros que preparas: nombres ("alpha_walking", "rough_walk_e", "rough_walk_g") o rutas a TUS .onnx.
#   AFECTA A: que politicas se comparan. Prueba tambien un .onnx que hayas exportado tu.
CEREBROS = ["alpha_walking", "rough_walk_e", "rough_walk_g"]

# Recorridos de 10 s por cada cerebro y nivel. Mas = mas fiable (y mas tiempo). Con 10 ya se ve la tendencia.
PRUEBAS = 10

# Hasta que nivel de perturbacion pruebas (0 a 5).
NIVEL_MAX = 5

# ---- Lo "sucio" de cada nivel (el robot real y el simulador nunca coinciden del todo) ----
ROZAMIENTO = (0.7, 1.3)        # nivel 1: el suelo agarra entre un 70 % y un 130 % de lo normal (el entrenamiento real aleatoriza lo mismo)
MASA = (0.8, 1.2)              # nivel 2: el robot pesa entre un 80 % y un 120 % (bateria, cables, piezas impresas...)
VOLTAJE_BAJO = 6.5             # nivel 3: voltios de bateria baja (llena = 7.4). Los motores empujan menos.
RETRASO = (1, 3)               # nivel 4: pasos de 20 ms que tardan en llegar las ordenes (1-3 = 20-60 ms)
EMPUJON = 0.3                  # nivel 5: velocidad (m/s) de un empujon al azar cada 3 s

# ====================================================================

import sim2real  # noqa: E402

if __name__ == "__main__":
    print(__doc__)
    t0 = time.time()
    print("=" * 78 + "\n 1 · CONTRATO DEL FICHERO\n" + "=" * 78)
    for c in CEREBROS:
        print(f"\n {c}")
        for nombre, ok, detalle in sim2real.contrato(c):
            print(f"   [{'OK' if ok else 'FALLA'}] {nombre:42s} {detalle}")
    niveles = tuple(range(NIVEL_MAX + 1))
    print("\n" + "=" * 78 + "\n 2 · ROBUSTEZ EN CRESCENDO  (caidas / recorridos de 10 s)\n" + "=" * 78)
    cab = f" {'nivel':32s}" + "".join(f"{str(c)[-16:]:>18s}" for c in CEREBROS)
    print(cab)
    resultados = {c: {} for c in CEREBROS}
    for c in CEREBROS:
        resultados[c] = sim2real.bateria(c, niveles=niveles, pruebas=PRUEBAS, rozamiento=ROZAMIENTO, masa=MASA,
                                         voltaje_bajo=VOLTAJE_BAJO, retraso=RETRASO, empujon=EMPUJON)
    for nv in niveles:
        print(f" {sim2real.NIVELES[nv]:32s}" + "".join(f"{str(resultados[c][nv]) + '/' + str(PRUEBAS):>18s}" for c in CEREBROS))
    print()
    for c in CEREBROS:
        sin_caidas = [nv for nv in niveles if all(resultados[c][k] == 0 for k in range(nv + 1))]
        ok = max(sin_caidas) if sin_caidas else -1
        veredicto = (f"sin caidas hasta el nivel {ok} ({sim2real.NIVELES[ok]})" if ok >= 0 else "se cae ya en el mundo ideal")
        print(f"   {c}: {veredicto}")
    print(f"\n[{time.time() - t0:.0f} s]  Cada nivel anade UNA perturbacion: el primero con caidas te dice QUE es lo que rompe a ese cerebro.\n")
    print("=" * 78 + "\n 3 · " + sim2real.LISTA_DESPLIEGUE.split("\n", 1)[0] + "\n" + "=" * 78)
    print(sim2real.LISTA_DESPLIEGUE.split("\n", 1)[1])
