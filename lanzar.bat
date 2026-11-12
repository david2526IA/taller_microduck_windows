@echo off
REM Uso:  lanzar.bat n4_00_partida_rayuela      (el nombre del ejercicio, sin .py)
REM Las teclas se pulsan en esta ventana negra, no en la ventana del robot.
cd /d "%~dp0"
if "%1"=="" (
  echo Uso: lanzar.bat NOMBRE_DEL_EJERCICIO   p. ej.  lanzar.bat n4_00_partida_rayuela
  dir /b exercises_rayuela\*.py
  pause
  exit /b
)
workshop-ia-fisica\.venv\Scripts\python.exe exercises_rayuela\%1.py %2 %3
pause
