@echo off
REM Reto por parejas. Cambia las opciones de la ultima linea y pulsa doble clic.
REM   --vin 6.5            bateria baja
REM   --delay 2 4          retraso en los motores
REM   --action-scale 0.7   motores menos potentes
REM   --walking policies\progresion_3_bien.onnx   otro cerebro
.venv\Scripts\python.exe scripts\infer_policy.py --walking policies\alpha_walking.onnx --standing policies\alpha_stand.onnx --sitstand policies\alpha_sitstand.onnx --roulade policies\roulade.onnx --new-cmd-obs --vin 6.5
pause
