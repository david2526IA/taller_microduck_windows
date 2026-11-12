# Preparacion del PC (Windows). Lo normal es hacer doble clic en INSTALAR.bat (llama a este script).
# A mano, desde la carpeta del repo:  powershell -ExecutionPolicy Bypass -File setup_windows.ps1
# No necesita permisos de administrador ni Git. Las librerias vienen en la carpeta wheels\ (sin Internet).
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
Write-Host "== 1/4 Comprobando Python 3.12 =="
$py = $null
try { & py -3.12 --version | Out-Null; if ($LASTEXITCODE -eq 0) { $py = "py -3.12" } } catch {}
if (-not $py) {
  Write-Host "Python 3.12 no encontrado. Intentando instalar con winget..."
  try { winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements } catch {}
  # El PATH de esta ventana no se actualiza solo: lo recargamos.
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
  try { & py -3.12 --version | Out-Null; if ($LASTEXITCODE -eq 0) { $py = "py -3.12" } } catch {}
  if (-not $py) {
    Write-Host "NO SE PUDO INSTALAR PYTHON 3.12. Instalalo a mano desde https://www.python.org/downloads/release/python-3120/ (64 bits, marcar 'Add python.exe to PATH') y vuelve a ejecutar."
    exit 1
  }
}
Write-Host "== 2/4 Creando entorno virtual .venv =="
Invoke-Expression "$py -m venv .venv"
if ($LASTEXITCODE -ne 0) { Write-Host "No se pudo crear .venv"; exit 1 }
$ErrorActionPreference = "Stop"
Write-Host "== 3/4 Instalando librerias (sin Internet, desde wheels\) =="
.\.venv\Scripts\python.exe -m pip install --no-index --find-links wheels -r requirements.txt
if ($LASTEXITCODE -ne 0) {
  Write-Host "Instalacion sin Internet fallida; probando con Internet (PyPI)..."
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  if ($LASTEXITCODE -ne 0) { Write-Host "NO SE PUDIERON INSTALAR LAS LIBRERIAS (ver mensajes de arriba)."; exit 1 }
}
Write-Host "== Extras: Visual C++, VS Code y sus extensiones (si faltan; no es grave si alguno falla) =="
try {
  $vc = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" -ErrorAction SilentlyContinue
  if (-not $vc -or $vc.Installed -ne 1) {
    Write-Host "Instalando Visual C++ Redistributable (puede pedir permiso de administrador)..."
    winget install -e --id Microsoft.VCRedist.2015+.x64 --accept-package-agreements --accept-source-agreements
  }
  $code = Get-Command code -ErrorAction SilentlyContinue
  if (-not $code -and -not (Test-Path "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd")) {
    Write-Host "Instalando Visual Studio Code..."
    winget install -e --id Microsoft.VisualStudioCode --scope user --accept-package-agreements --accept-source-agreements
  }
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
  # Con ErrorActionPreference=Stop, un simple aviso de 'code' (stderr) se convertia en excepcion y saltaba Pylance.
  $ErrorActionPreference = "Continue"
  foreach ($ext in "ms-python.python", "ms-python.vscode-pylance") { code --install-extension $ext --force 2>&1 | Out-Null }
  $ErrorActionPreference = "Stop"
} catch { Write-Host "Aviso: algun extra no se pudo instalar ($($_.Exception.Message)). Instalarlo a mano." }
$ErrorActionPreference = "Stop"
Write-Host "== 4/4 Verificando =="
.\.venv\Scripts\python.exe check_setup.py
exit $LASTEXITCODE
