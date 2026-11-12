@echo off
REM Doble clic: la ruta guiada del taller, paso a paso.
cd /d "%~dp0"
chcp 65001 >nul
workshop-ia-fisica\.venv\Scripts\python.exe ruta.py
pause
