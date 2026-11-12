# Taller Microduck · proyecto Windows

Todo el taller a mano en VS Code. Este repo solo contiene el "envoltorio"; los tres repos reales se descargan dentro.

## Empezar (Windows)
1. Crea una carpeta **corta** (p. ej. en el Escritorio) y clona esto dentro:
   ```
   git clone https://github.com/david2526IA/taller_microduck_windows taller_microduck_upskill_winodws
   cd taller_microduck_upskill_winodws
   ```
2. Doble clic en **`INSTALAR_TODO.bat`** (clona los 3 repos y prepara Python 3.12 + MuJoCo; ~3 min).
3. Doble clic en **`ABRIR_EN_VSCODE.bat`**.
4. Comprueba: en `workshop-ia-fisica`, `COMPROBAR.bat` debe acabar en **TODO LISTO**.

**Para probar el taller entero, ejercicio por ejercicio y con todos sus parámetros: [`PROBAR.md`](PROBAR.md).** Los ejercicios nuevos están en `exercises_rayuela/`.

## Qué se descarga
| Carpeta | Contenido |
|---|---|
| `workshop-ia-fisica/` | Proyecto de los asistentes (empieza por `TALLER.md`) |
| `workshop-ia-fisica-ponente/` | Material del ponente |
| `taller_microduck_v2/` | Copia completa con entrenamientos |

## Notas Windows
- Los repos privados piden iniciar sesión en GitHub (`gh auth login`).
- `parches/setup_windows.ps1` corrige un falso aviso al instalar las extensiones de VS Code; `clonar_todo.ps1` lo aplica.
- Si el Escritorio está en OneDrive, pausa la sincronización: los repos y `.venv` pesan >1 GB.
