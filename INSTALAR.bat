@echo off
REM Doble clic para preparar este PC (Python 3.12 + MuJoCo + OpenCV + cerebros). No necesita administrador ni internet.
cd /d "%~dp0"
echo ===== Instalando el entorno del taller. Puede tardar 2-3 minutos. NO toques el teclado hasta que acabe =====
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0workshop-ia-fisica\setup_windows.ps1" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath instalar_log.txt"
echo.
echo ===== Comprobando todo el taller =====
workshop-ia-fisica\.venv\Scripts\python.exe check_taller.py 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath instalar_log.txt -Append"
echo.
echo Si arriba pone TODO LISTO, el PC esta preparado. Si no, enviar instalar_log.txt al ponente.
pause
