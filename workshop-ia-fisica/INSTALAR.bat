@echo off
REM Doble clic para preparar este PC (Python 3.12 + MuJoCo + politicas). No necesita administrador.
cd /d "%~dp0"
echo ===== Instalando el entorno del taller. Puede tardar 2-3 minutos =====
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath instalar_log.txt"
echo.
echo Si arriba pone TODO LISTO, el PC esta preparado. Si no, enviar instalar_log.txt al ponente.
pause
