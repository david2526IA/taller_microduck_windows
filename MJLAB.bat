@echo off
REM Doble clic: abre una consola con el mini-mjlab (list-envs, params, play, train, validate). Sin GPU.
cd /d "%~dp0"
chcp 65001 >nul
workshop-ia-fisica\.venv\Scripts\python.exe mini_mjlab.py list-envs
echo.
echo Ejemplos:  MJLAB play Mini-Obstacles-MicroDuck --set NIVEL=3 --set CEREBRO=rough_walk_e
echo.
cmd /k
