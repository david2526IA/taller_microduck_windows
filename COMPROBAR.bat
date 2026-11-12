@echo off
REM Doble clic: comprueba todo el taller y abre el visor 5 segundos.
cd /d "%~dp0"
workshop-ia-fisica\.venv\Scripts\python.exe check_taller.py --viewer
pause
