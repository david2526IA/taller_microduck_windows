@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File clonar_todo.ps1
pause

