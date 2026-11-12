@echo off
REM Demo completa: andar, quedarse de pie, sentarse, rodar. Controles en la terminal.
REM Flechas = velocidad | A/E = girar | Y = sentarse/levantarse | R = voltereta | Espacio = parar | Q = salir
.venv\Scripts\python.exe scripts\infer_policy.py --walking policies\alpha_walking.onnx --standing policies\alpha_stand.onnx --sitstand policies\alpha_sitstand.onnx --roulade policies\roulade.onnx --new-cmd-obs %*
