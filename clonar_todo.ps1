# Descarga los 3 repos del taller dentro de esta carpeta, aplica el parche de Windows y prepara el entorno.
# Uso (desde esta carpeta):  powershell -ExecutionPolicy Bypass -File clonar_todo.ps1 [-SinInstalar]
param([switch]$SinInstalar)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
git config --global core.longpaths true   # evita "Filename too long" en Windows
# nombre local = repo remoto (el oficial de Rayuela y el de la cuerda se clonan con otro nombre de carpeta)
$repos = @(
  @("workshop-ia-fisica",          "https://github.com/david2526IA/workshop-ia-fisica"),
  @("workshop-ia-fisica-ponente",  "https://github.com/david2526IA/workshop-ia-fisica-ponente"),
  @("taller_microduck_v2",         "https://github.com/david2526IA/taller_microduck_v2"),
  @("rayuela-oficial",             "https://github.com/Bravo-Robots/microduck_rl-rayuela"),
  @("tug-of-war",                  "https://github.com/david2526IA/microduck-tug-of-war")
)
foreach ($r in $repos) {
  if (Test-Path $r[0]) { Write-Host "== $($r[0]) ya existe: git pull"; git -C $r[0] pull --ff-only }
  else { Write-Host "== Clonando $($r[0])"; git clone $r[1] $r[0] }
}
Copy-Item parches\setup_windows.ps1 workshop-ia-fisica\setup_windows.ps1 -Force
if (-not $SinInstalar) {
  Write-Host "== Preparando el entorno (Python 3.12, sin internet)"
  powershell -NoProfile -ExecutionPolicy Bypass -File workshop-ia-fisica\setup_windows.ps1
  # OpenCV: lo necesita el nodo de VISION de la Rayuela (necesita internet; el resto del taller no)
  Write-Host "== Instalando OpenCV (vision de la Rayuela)"
  workshop-ia-fisica\.venv\Scripts\python.exe -m pip install --quiet opencv-python
}
Write-Host "`nListo. Abre el proyecto con:  code taller_microduck.code-workspace"
