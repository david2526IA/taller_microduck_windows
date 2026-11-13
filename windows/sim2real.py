"""PREPARAR EL SIM-TO-REAL: antes de llevar una politica al robot, comprobar su CONTRATO y su ROBUSTEZ en simulacion.

El salto de la simulacion al robot real (la "brecha") falla por motivos conocidos: el suelo no agarra igual, el robot pesa un poco
distinto, la bateria cae, las ordenes llegan con retraso y alguien lo empuja. Se prepara asi (la receta de NVIDIA y Pollen con el Microduck):
  1. CONTRATO: el fichero .onnx tiene la forma que espera el robot (61 entradas -> 14 salidas, decimales de 32 bits, <= 64 MiB).
  2. ROBUSTEZ en crescendo (aleatorizacion del dominio): se prueba la politica con un mundo cada vez mas "sucio" y se cuentan caidas.
     Si aguanta, entrenar con ese azar es lo que la hizo fiable; si no, hay que entrenar con mas aleatorizacion.
  3. LISTA de despliegue: los pasos para copiarla al robot y volver atras.
Todo en simulacion y en CPU. No se ha probado nunca con el robot real: es la preparacion, no la prueba final.
"""
import contextlib, io, math, os, pathlib, sys

import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI / "windows"))
import obstaculos  # noqa: E402  (carga el codigo oficial y conoce los cerebros)

NIVELES = [
    "0 · mundo ideal", "1 · + rozamiento al azar", "2 · + masa al azar", "3 · + bateria baja",
    "4 · + retraso en los motores", "5 · + empujones",
]
MAX_MIB = 64


def _ruta(cerebro):
    return pathlib.Path(cerebro) if os.path.exists(str(cerebro)) else obstaculos.CEREBROS[cerebro]


def contrato(cerebro):
    """Comprueba la forma del .onnx. Devuelve una lista de (comprobacion, ok, detalle)."""
    import onnxruntime as ort
    ruta = _ruta(cerebro)
    out = []
    mib = ruta.stat().st_size / 2 ** 20
    out.append(("tamano <= 64 MiB", mib <= MAX_MIB, f"{mib:.2f} MiB"))
    s = ort.InferenceSession(str(ruta))
    ent, sal = s.get_inputs()[0], s.get_outputs()[0]
    out.append(("entrada de 61 numeros", list(ent.shape)[-1] == 61, f"{ent.name} {ent.shape} {ent.type}"))
    out.append(("salida de 14 ordenes", list(sal.shape)[-1] == 14, f"{sal.name} {sal.shape} {sal.type}"))
    out.append(("decimales de 32 bits", "float" in ent.type and "float" in sal.type, f"{ent.type} -> {sal.type}"))
    try:
        a = s.run(None, {ent.name: np.zeros((1, 61), np.float32)})[0]
        out.append(("responde con numeros finitos", bool(np.all(np.isfinite(a))), f"salida de ejemplo en [{a.min():.2f}, {a.max():.2f}]"))
        out.append(("ordenes de tamano razonable (|a| < 10)", bool(np.abs(a).max() < 10), f"max |a| = {np.abs(a).max():.2f}"))
    except Exception as e:
        out.append(("responde a una entrada", False, str(e)[:80]))
    return out


def bateria(cerebro, niveles=(0, 1, 2, 3, 4, 5), pruebas=10, avance=0.3, segundos=10.0, semilla=0,
            rozamiento=(0.7, 1.3), masa=(0.8, 1.2), voltaje_bajo=6.5, retraso=(1, 3), empujon=0.3):
    """Prueba la politica en 'pruebas' recorridos de 'segundos' s por nivel (como la bateria de Pollen: 10 s a 0,3 m/s).
    Cada nivel anade UNA perturbacion. Devuelve {nivel: caidas}."""
    import mujoco
    ip = obstaculos._cargar_oficial()
    ruta = _ruta(cerebro)
    rng = np.random.default_rng(semilla)
    modelos = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for vin in sorted({7.4, voltaje_bajo}):
            bam = ip.load_bam_model(ip.BAM_KP_FW, vin, 0.0)
            m, d, ctrl, _ = ip.load_mujoco_with_bam(str(obstaculos.ESCENA), bam, 0.005, 0.1, ip.BAM_VIN_MIN)
            geoms = [i for i in range(m.ngeom) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i) or "") in
                     ("floor", "left_foot_collision", "right_foot_collision")]
            modelos[vin] = (m, d, ctrl, geoms, m.geom_friction.copy(), m.body_mass.copy(), m.body_inertia.copy())
    standing = str(obstaculos.CEREBROS["alpha_walking"]).replace("walking", "standing")
    res = {}
    for nv in niveles:
        caidas = 0
        for k in range(pruebas):
            vin = voltaje_bajo if nv >= 3 else 7.4
            m, d, ctrl, geoms, fr0, ma0, in0 = modelos[vin]
            m.geom_friction[:] = fr0
            m.body_mass[:] = ma0
            m.body_inertia[:] = in0
            if nv >= 1:
                for g in geoms:
                    m.geom_friction[g, 0] = fr0[g, 0] * rng.uniform(*rozamiento)
            if nv >= 2:
                f = rng.uniform(*masa)
                m.body_mass[:] = ma0 * f
                m.body_inertia[:] = in0 * f
            lag = (int(retraso[0]), int(retraso[1])) if nv >= 4 else (0, 0)
            mujoco.mj_resetData(m, d)
            with contextlib.redirect_stdout(io.StringIO()):
                pol = ip.PolicyInference(m, d, bam_ctrl=ctrl, walking_onnx_path=str(ruta), standing_onnx_path=standing,
                                         action_scale=1.0, delay_min_lag=lag[0], delay_max_lag=lag[1], switch_threshold=0.1,
                                         use_projected_gravity=True, new_cmd_obs=True)
                adr = m.jnt_qposadr[m.joint("trunk_base_freejoint").id]
                dof = m.jnt_dofadr[m.joint("trunk_base_freejoint").id]
                cuerpo = m.body("trunk_base").id
                d.qpos[adr:adr + 3] = [0, rng.uniform(-0.05, 0.05), 0.125]
                d.qpos[adr + 3:adr + 7] = [1, 0, 0, 0]
                for i, q in enumerate(pol.joint_qpos_indices):
                    d.qpos[q] = pol.default_pose[i]
                ctrl.reset(d.qpos)
                pol.set_position_targets(pol.default_pose)
                mujoco.mj_forward(m, d)
                cayo = False
                for paso in range(int(segundos / 0.02)):
                    if paso % 5 == 0:
                        pol.set_vel_cmd(avance, 0.0, obstaculos.rumbo_wz(d, cuerpo))
                    if nv >= 5 and paso % 150 == 75:                      # un empujon al azar cada 3 s
                        ang = rng.uniform(0, 2 * math.pi)
                        d.qvel[dof] += empujon * math.cos(ang)
                        d.qvel[dof + 1] += empujon * math.sin(ang)
                    pol.apply_action(pol.infer())
                    for _ in range(4):
                        ctrl.update()
                        mujoco.mj_step(m, d)
                    tilt = math.degrees(math.acos(max(-1.0, min(1.0, d.xmat[cuerpo][8]))))
                    if tilt > 55 or d.xpos[cuerpo][2] < 0.05:
                        cayo = True
                        break
            caidas += cayo
        res[nv] = caidas
    return res


LISTA_DESPLIEGUE = """LISTA PARA LLEVARLA AL ROBOT (la receta de NVIDIA / Pollen para el Microduck; aqui NO se ejecuta, no hay robot):
  1. Exporta tu politica a ONNX (el entrenamiento de mjlab / Isaac Lab ya lo hace al terminar: exported/policy.onnx).
  2. Pasa el CONTRATO de arriba: 61 entradas, 14 salidas, float32, <= 64 MiB.
  3. Pasa la BATERIA de robustez: sin caidas en los niveles que el robot real va a sufrir (rozamiento, masa, bateria, retraso).
  4. Copia el fichero al robot:   scp policy.onnx <usuario>@<robot>:/home/<usuario>/policies/mi_andar.onnx
  5. Cargala como la politica de andar:   sudo robotctl policy load walk /home/<usuario>/policies/mi_andar.onnx
  6. Observa:   robotctl monitor        Para volver a la de fabrica:   sudo robotctl policy reset walk
  7. Primera prueba: suelo liso; luego el borde de una alfombra; luego una rampa suave. Apunta la ruta de la politica de fabrica para volver en un paso.
  8. Si falla en el robot y no en simulacion: sube la aleatorizacion (mas rozamiento, masa, retraso, empujones) y vuelve a entrenar.
(Fuente: tutorial de NVIDIA "Microduck + Isaac Lab, sim-to-real" y la ficha de las politicas rough-walk de Hugging Face.)"""
