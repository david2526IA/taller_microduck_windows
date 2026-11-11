# Descarga los 3 repos del taller dentro de esta carpeta, aplica el parche de Windows y prepara el entorno.
# Uso (desde esta carpeta):  powershell -ExecutionPolicy Bypass -File clonar_todo.ps1 [-SinInstalar]
param([switch]$SinInstalar)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
git config --global core.longpaths true   # evita "Filename too long" en Windows
foreach ($r in "workshop-ia-fisica", "workshop-ia-fisica-ponente", "taller_microduck_v2") {
  if (Test-Path $r) { Write-Host "== $r ya existe: git pull"; git -C $r pull --ff-only }
  else { Write-Host "== Clonando $r"; git clone "https://github.com/david2526IA/$r" }
}
Copy-Item parches\setup_windows.ps1 workshop-ia-fisica\setup_windows.ps1 -Force
if (-not $SinInstalar) {
  Write-Host "== Preparando el entorno (Python 3.12, sin internet)"
  powershell -NoProfile -ExecutionPolicy Bypass -File workshop-ia-fisica\setup_windows.ps1
}
Write-Host "`nListo. Abre el proyecto con:  code taller_microduck.code-workspace"
