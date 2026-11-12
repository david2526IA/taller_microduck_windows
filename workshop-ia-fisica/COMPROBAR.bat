@echo off
REM Doble clic: abre el visor 3D del robot durante 5 s para comprobar graficos.
cd /d "%~dp0"
.venv\Scripts\python.exe check_setup.py --viewer
pause
